import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";
import ReactPaginate from 'react-paginate';
import DeleteVideo from "./DeleteVideo";

class Camera extends Component {
	state = {
			data: [],
			showVideo: false,
			videoFile: "",
			videoTitle: "",
			showDelete: false,
			deleteIdentifier: "",
			deleteDescription: "",
			fetching: false,
			delay: 5000,
			offset: 0,
		      perPage: 5,
		      currentPage: 0};

	componentDidMount() {
		this.fetchData();
//		this.interval = setInterval(this.fetchData, this.state.delay);
	}
		
	componentWillUnmount() {
//		clearInterval(this.interval);
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
							fetching: false,
							pageCount: Math.ceil(response.length / this.state.perPage)});
			});
	}
	
	popupVideo() {
		return <div className="modal is-active">
		<div className="modal-background" />
			<div className="modal-card">
			<header className="modal-card-head">
				<p className="modal-card-title">{this.state.videoTitle}</p>
				<button className="delete" onClick={() => this.hideVideo()} />
			</header>
			<section className="modal-card-body">
				<div className="content">
					<video width="720" height="480" controls>
						<source src={"camera/" + this.state.videoFile} type="video/mp4" />
					</video>
				</div>
			</section>
			</div>
		</div>;
	}

	paginationControls() {
		return <div>
        <ReactPaginate
            previousLabel={"prev"}
            nextLabel={"next"}
            breakLabel={"..."}
            breakClassName={"break-me"}
            pageCount={this.state.pageCount}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            containerClassName={"pagination"}
            subContainerClassName={"pages pagination"}
            activeClassName={"active"}/>
        </div>;
	}
	
	showVideo(video) {
		this.setState({
			showVideo: true, 
			videoFile: video.fileName,
			videoTitle: this.videoDescription(video)})
	}
	
	hideVideo() {
		this.setState({
			showVideo: false, 
			videoFile: "", 
			videoTitle: ""})
	}
	
	showDeleteVideo(video) {
		this.setState({
			showDelete: true, 
			deleteIdentifier: video.identifier,
			deleteDescription: this.videoDescription(video)})
	}
	
	hideDeleteVideo() {
		this.setState({
			showDelete: false, 
			deleteIdentifier: "", 
			deleteDescription: ""})
	}
	
	updateVideosList() {
		var filterDeletedVideo = this.state.data.filter(video => video.identifier != this.state.deleteIdentifier);
		this.setState({
			showDelete: false, 
			deleteIdentifier: "", 
			deleteDescription: "",
			data: filterDeletedVideo})
	}

	videoDescription(video) {
		var dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
				hour: 'numeric', minute: 'numeric', second: 'numeric', 
				hour12: false, weekday: 'long'};
		return new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(video.dateCreated));
	}
	
	getPopupToShow() {
		var popup;
		if (this.state.showVideo) {
			popup = this.popupVideo();
		} else if (this.state.showDelete) {
			popup = <DeleteVideo
						identifier = {this.state.deleteIdentifier}
						description =  {this.state.deleteDescription}
						cancel = {() => this.hideDeleteVideo()}
						confirm = {() => this.updateVideosList()} />
		}
		return popup;
	}
	
	render() {
		if (!this.state.data || this.state.data.length == 0) {
			return (<div className="has-text-centered">No hay archivos multimedia</div>);
		}

		var popup = this.getPopupToShow();
		var pag = this.paginationControls();

		var lastVideo = this.state.data[0];
		var currentSituation = <a href="#" onClick={() => this.showVideo(lastVideo)}>{this.videoDescription(lastVideo)}</a>;
		
		return <div>
				{popup}
				<div className="notification has-text-black">
					<p>Situación actual</p>
					{currentSituation}
				</div>
				<p>Detecciones</p>
				<ul className="has-text-centered">  
				{this.state.data.map(video => (
					<li key={video.id} className={video.peopleDetected ? "notification has-text-black is-danger" : "notification has-text-black is-grey"}>
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
				{pag}
			</div>;
	}
}
export default Camera;