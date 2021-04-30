import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";
import ReactPaginate from 'react-paginate';
import DeleteVideo from "./DeleteVideo";
import ShowVideo from "./ShowVideo";

class Camera extends Component {
	state = {
			data: [],
			video: null,
			showVideo: false,
			showDelete: false,
			fetching: false,
			delay: 5000,
			offset: 0,
		      perPage: 2,
		      currentPage: 1};

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
	
	paginationControls() {
		return <div className="pagination">
		        <ReactPaginate
			        breakClassName={''}
			        breakLinkClassName={'has-text-white'}
			        containerClassName={'pagination-list'}
			        pageClassName={'pagination-link'}
			        pageLinkClassName={'has-text-white'}
			        previousClassName={'pagination-previous'}
			        previousLinkClassName={'has-text-white'}
			        nextClassName={'pagination-next'}
			        nextLinkClassName={'has-text-white'}
			        activeClassName={'is-current'}
		            previousLabel={"<"}
		            nextLabel={">"}
		            breakLabel={"..."}
		            pageCount={this.state.pageCount}
		            marginPagesDisplayed={2}
		            pageRangeDisplayed={5}/>
		        </div>;
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
		var filterDeletedVideo = this.state.data.filter(video => video.identifier != this.state.deleteIdentifier);
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
			return (<div className="has-text-centered">No hay archivos multimedia</div>);
		}

		var popup = this.popUp();
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
					<li key={video.id} className={video.classification == "person" ? "notification has-text-black is-danger" : "notification has-text-black is-grey"}>
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