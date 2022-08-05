import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";

class Buttons extends Component {
  static propTypes = {
	  data: PropTypes.array.isRequired
  };
  state = {
		  data: this.props.data
  };
  
  executeaction(action) {
	var url = 'executeaction/';
	
	var data = {action: action.id, priority: 1, duration:3600, who: 'manual'};
	
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + 'csrftoken' + '=');
    
    if (parts.length == 2) {
    	var csrftoken = parts.pop().split(";").shift();
    }
	
	fetch(url, {
	  method: 'POST',
	  body: JSON.stringify(data),
	  headers:{
	    'Content-Type': 'application/json',
	    'X-CSRFToken': csrftoken
	  }
	}).then(res => {
		if (res.ok) 
			return res.json();
		else
			throw new Error(res.status + ' ' + res.statusText);})
	.catch(error => console.error('Error:', error))
	.then(response => {
		if(response) {
			action.status = response.status;
			action.durationOn = (response.status ? response.duration : 0);
			action.durationOff = (!response.status ? response.duration : 0);
			this.setState({data: this.state.data})
		}
	});
  }
  
  componentDidUpdate() {
	  if (this.state.data !== this.props.data) {
		  this.setState({data: this.props.data});
	  }
  }
  
  showActionExpiration(action) {
	  if (action.status) {
		  if(action.durationOn > 0) {
			  return "Se apagará automáticamente en " + new Date(action.durationOn * 1000).toISOString().substr(11, 8);
		  } else {
			  return "";
		  }
	  }
	  return "";
  }
  
  render() {
	  if (!this.state.data || this.state.data.length == 0) {
		return <div className="has-text-centered">No hay controles configurados</div>;
	  }
	  // check if data is right for this rendering
	  let sample = this.state.data[0];
	  if (!sample.id) {  
		return "";
	  }
	  return <ul className="has-text-centered">  
	  {this.state.data.map(action => (
			  <li key={action.id} className={action.status ? "notification is-turned-on" : "notification"}>
	  		  <button className="button" key={action.id} onClick={() => this.executeaction(action)}>
	  		  {action.description}
	  		  </button>
	  		  <p className="has-text-black">{this.showActionExpiration(action)}</p>
	  		  </li>
	  		  ))}
	  		</ul>;
  }
}
export default Buttons;