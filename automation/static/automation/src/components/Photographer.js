import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";
import ShowPhoto from "./ShowPhoto";

class Photographer extends Component {
	state = {
			data: [],
			photo: null,
			showPhoto: false,
			fetching: false,
			delay: 10000};

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
		fetch('media/').then(res => {
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

	deleteMedia = () => {
		var url = 'deleteallmedia/';
		
		const value = '; ' + document.cookie;
		const parts = value.split('; ' + 'csrftoken' + '=');
		
		if (parts.length == 2) {
			var csrftoken = parts.pop().split(";").shift();
		}
		
		fetch(url, {
			method: 'POST',
			body: "",
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
				this.fetchData();
			}
		});	
	}

	showPhoto(photo) {
		this.setState({
			photo: photo,
			showPhoto: true})
	}
	
	hidePhoto() {
		this.setState({
			photo: null,
			showPhoto: false})
	}
	
	popUp() {
		var popup;
		if (this.state.showPhoto) {
			popup = <ShowPhoto 
						photo = {this.state.photo}
						close = {() => this.hidePhoto()} />
		}
		return popup;
	}
	
	photoDescription(photo) {
		var dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
				hour: 'numeric', minute: 'numeric', second: 'numeric', 
				hour12: false, weekday: 'long'};
		var description = '';
		if (photo.classification) {
			description += photo.classification + ' - ';
		}
		description += new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(photo.dateCreated));
		return description;
	}
	
	render() {
		if (!this.state.data || this.state.data.length == 0) {
			return (<div className="has-text-centered has-text-white">No hay archivos multimedia</div>);
		}
		var popup = this.popUp();

		return <div>
				{popup}
				<div>
					<label className="label has-text-white">{this.state.data.length + " archivos"}</label>
					<button className="button is-danger" onClick={() => this.deleteMedia()}>Borrar todo</button>
				</div>
				<div className="columns is-multiline">
				{this.state.data.map(photo => (
					<div className="column is-one-quarter-desktop is-half-tablet" key={photo}>
					  <div className="card">
					      <div className="card-image">
					          <figure className="image is-3by2">
					            <img src={"camera/" + photo.thumbnail} alt="" />
					          </figure>
							  <div className="card-content is-overlay is-clipped">
							    <span className="tag is-info">
						            <a className="has-text-white" href="#" onClick={() => this.showPhoto(photo)}>
										{this.photoDescription(photo)}
									</a>
							    </span>       
							  </div>					          
					      </div>
					  </div>
					</div>
					))}
				</div>
			</div>;
	}
}
export default Photographer;