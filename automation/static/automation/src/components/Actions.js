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
  
  executeaction(el) {
	var url = 'executeaction/';
	
	var data = {action: el.id, priority: 1, duration:15};
	
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
			el.status = response.status;
			this.setState({data: this.state.data})
		}
	});
  }
  
  componentDidUpdate() {
	  if (this.state.data !== this.props.data) {
		  this.setState({data: this.props.data});
	  }
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
	  {this.state.data.map(el => (
			  <li key={el.id} className={el.status ? "notification is-turned-on" : "notification"}>
	  		  <button className="button" key={el.id} onClick={() => this.executeaction(el)}>
	  		  {el.description}
	  		  </button>
	  		  </li>
	  		  ))}
	  		</ul>;
  }
}
export default Buttons;