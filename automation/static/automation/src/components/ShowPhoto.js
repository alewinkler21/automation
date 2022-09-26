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
		  
	render() {
		return <div className="modal is-active">
		<div className="modal-background" />
			<div className="modal-card">
			<header className="modal-card-head">
				<p className="modal-card-title">{this.state.photo}</p>
				<button className="delete" onClick={() => this.props.close()} />
			</header>
			<section className="modal-card-body">
				<div className="content">
					<img src={"camera/" + this.state.photo} alt="" />
				</div>
			</section>
			</div>
		</div>;
	}
}
export default ShowPhoto;