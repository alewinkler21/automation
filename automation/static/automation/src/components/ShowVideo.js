import React, { Component } from "react";
import PropTypes from "prop-types";

class ShowVideo extends Component {
	static propTypes = {
		video: PropTypes.object.isRequired,
		close: PropTypes.func.isRequired
	};
	state = {
			video: this.props.video
			};
	
	videoDescription() {
		var dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
				hour: 'numeric', minute: 'numeric', second: 'numeric', 
				hour12: false, weekday: 'long'};
		return new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(this.state.video.dateCreated));
	}
	  
	render() {
		return <div className="modal is-active">
		<div className="modal-background" />
			<div className="modal-card">
			<header className="modal-card-head">
				<p className="modal-card-title">{this.videoDescription()}</p>
				<button className="delete" onClick={() => this.props.close()} />
			</header>
			<section className="modal-card-body">
				<div className="content">
					<video width="720" height="480" controls>
						<source src={"camera/" + this.state.video.videoFile} type="video/mp4" />
					</video>
				</div>
			</section>
			</div>
		</div>;
	}
}
export default ShowVideo;