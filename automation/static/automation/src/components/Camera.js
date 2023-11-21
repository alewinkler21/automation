import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";
import DeleteVideo from "./DeleteVideo";
import ShowVideo from "./ShowVideo";

class Camera extends Component {
	state = {
			data: [],
			video: null,
			showVideo: false,
			showDelete: false,
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
	
	showVideo(video) {
		this.setState({
			video: video,
			showVideo: true})
	}
	
	hideVideo() {
		this.setState({
			video: null,
			showVideo: false})
	}
	
	showDeleteVideo(video) {
		this.setState({
			video: video,
			showDelete: true})
	}
	
	hideDeleteVideo() {
		this.setState({
			video: null,
			showDelete: false})
	}
	
	updateVideosList() {
		var filterDeletedVideo = this.state.data.filter(video => video.id != this.state.video.id);
		this.setState({
			video: null,
			showDelete: false,
			data: filterDeletedVideo})
	}

	videoDescription(video) {
		var dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
				hour: 'numeric', minute: 'numeric', second: 'numeric', 
				hour12: false, weekday: 'long'};
		return new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(video.dateCreated));
	}
	
	popUp() {
		var popup;
		if (this.state.showVideo) {
			popup = <ShowVideo 
						video = {this.state.video}
						close = {() => this.hideVideo()} />
		} else if (this.state.showDelete) {
			popup = <DeleteVideo
						video = {this.state.video}
						cancel = {() => this.hideDeleteVideo()}
						confirm = {() => this.updateVideosList()} />
		}
		return popup;
	}
	
	render() {
		if (!this.state.data || this.state.data.length == 0) {
			return (<div className="has-text-centered has-text-white">No hay archivos multimedia</div>);
		}
		var popup = this.popUp();		
		return <div>
				{popup}
				<ul className="has-text-centered">  
				{this.state.data.slice(1).map(video => (
					<li key={video.id} className="notification has-text-black is-grey">
					<div className="columns is-mobile">
						<div className="column">
							<a href="#" onClick={() => this.showVideo(video)}>
								{this.videoDescription(video)};
							</a>
						</div>
						<div className="column is-1">
							<a className="delete is-medium" href="#" onClick={() => this.showDeleteVideo(video)}>
							</a>
						</div>
					</div>
					</li>
					))}
				</ul>
			</div>;
	}
}
export default Camera;