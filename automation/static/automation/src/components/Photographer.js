import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";

class Photographer extends Component {
	state = {
			data: [],
			fetching: false,
			delay: 5000};

	componentDidMount() {
		this.fetchData();
		this.interval = setInterval(this.fetchData, this.state.delay);
	}
		
	componentWillUnmount() {
		clearInterval(this.interval);
	}
	
	fetchData = () => {
		if (this.state.fetching) {
			console.log('already fetching data');
			return;
		}
		this.setState({fetching: true});
		fetch('photographer/').then(res => {
			if (res.ok) 
				return res.json();
			else
				throw new Error(res.status + ' ' + res.statusText);})
		.catch(error => console.error('Error:', error))
		.then(response => {
			this.setState({data: response, 
							fetching: false});
			});
	}
		
	render() {
		if (!this.state.data || this.state.data.length == 0) {
			return (<div className="has-text-centered">No hay archivos multimedia</div>);
		}

		return <div className="columns is-multiline">
				{this.state.data.map(photo => (
					<div className="column is-one-quarter-desktop is-half-tablet">
					  <div className="card">
					      <div className="card-image">
					          <figure className="image is-3by2">
					            <img src={"camera/" + photo} alt="" />
					          </figure>
					      </div>
					  </div>
					</div>
					))}
			</div>;
	}
}
export default Photographer;