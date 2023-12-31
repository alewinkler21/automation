import React, { Component } from "react";
import PropTypes from "prop-types";

class DataProvider extends Component {
  static propTypes = {
    endpoint: PropTypes.string.isRequired,
    render: PropTypes.func.isRequired
  };
  state = {
      data: [],
      loaded: false,
      placeholder: "Loading..."
  };
  fetchData(){
	fetch(this.props.endpoint)
	  .then(response => {
	    if (response.status !== 200) {
	      return this.setState({ data: [], placeholder: "Something went wrong" });
	    }
	    return response.json();
	  })
	  .then(data => {
		  this.setState({ data: data, loaded: true })
	  });	  
  }
  
  componentDidMount() {
    this.fetchData();
    this.intervalID = setInterval(() => this.fetchData(), 5000);
  }
    
  componentWillUnmount(){
    clearInterval(this.intervalID);
  }

  componentDidUpdate(prevProps) {
	  if (this.props.endpoint !== prevProps.endpoint) {
		  this.fetchData();
	  }
  }
  render() {
    const { data, loaded, placeholder} = this.state;
    return loaded ? this.props.render(data) : <div className="column">{ placeholder }</div>;
  }
}
export default DataProvider;