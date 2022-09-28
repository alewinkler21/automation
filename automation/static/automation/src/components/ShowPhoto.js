import React, { Component } from "react";
import PropTypes from "prop-types";

class ShowPhoto extends Component {
	static propTypes = {
		photo: PropTypes.object.isRequired,
		close: PropTypes.func.isRequired
	};
	state = {
			photo: this.props.photo
			};
			
	photoDescription() {
		var dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
				hour: 'numeric', minute: 'numeric', second: 'numeric', 
				hour12: false, weekday: 'long'};
		return new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(this.state.photo.dateCreated));
	}
	
    share(){
		var url = "https://micamara.ddns.net:8443/camera/" + this.state.photo.thumbnail;
        if (navigator.share) {
          navigator.share({
            title: 'Compartir foto',
            url: url
          }).catch(console.error);
        } else {
            window.location.href = "mailto:?subject=Check this opportunity&body=<a href='" + encodeURIComponent(url) + "'>link</a>";
        }
    }
		  
	render() {
		return <div className="modal is-active">
		<div className="modal-background" />
			<div className="modal-card">
			<header className="modal-card-head">
				<button className="button" onClick={() => this.share()}>
					<span className="icon">
					  <i className="fas fa-share" ></i>
					</span>
				</button>
				<p className="modal-card-title">{this.photoDescription()}</p>
				<button className="delete" onClick={() => this.props.close()} />
			</header>
			<section className="modal-card-body">
				<div className="content">
					<img src={"camera/" + this.state.photo.thumbnail} alt="" />
				</div>
			</section>
			</div>
		</div>;
	}
}
export default ShowPhoto;