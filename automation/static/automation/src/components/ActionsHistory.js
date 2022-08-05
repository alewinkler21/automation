import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";

class History extends Component {
  static propTypes = {
	  data: PropTypes.array.isRequired
  };
  state = {
		  data: this.props.data
  };
  
  componentDidUpdate() {
	  if (this.state.data !== this.props.data) {
		  this.setState({data: this.props.data});
	  }
  }
    
  render() {
	  if (!this.state.data || this.state.data.length == 0) {
		return <div className="has-text-centered">No hay historial de acciones</div>;
	  }
	  // check if data is right for this rendering
	  let sample = this.state.data[0];
	  if (!sample.action) {  
		return "";
	  }
	  return <ul className="has-text-centered">  
	  {this.state.data.map(actionHistory => (
			  <li key={actionHistory.id} className={actionHistory.status ? "notification is-turned-on" : "notification"}>
	  		  {actionHistory.action.description} - {new Date(actionHistory.date).toLocaleString()} - {actionHistory.who}
	  		  </li>
	  		  ))}
	  		</ul>;
  }
}
export default History;