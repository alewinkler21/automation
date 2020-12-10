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
  
  toggleRelay(el) {
	if (el.simulationEnabled) {
		alert('No se puede utilizar manualmente cuando la simulación está activada. Desactive la simulación.');
		return;
	}
	var url = 'togglerelay/';
	
	var data = {relay: el.id, dateOfUse: new Date().toISOString(), status: !el.status};

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
		return <div className="column">No hay controles configurados</div>;
	  }	  
	  return <ul className="column has-text-centered">  
	  {this.state.data.map(el => (
			  <li key={el.id}>
	  		  <button className={el.status ? "button is-success" : "button is-black"} key={el.id} onClick={() => this.toggleRelay(el)}>
	  		  {el.name}
	  		  </button>
	  		  </li>
	  		  ))}
	  		</ul>;
  }
}
export default Buttons;