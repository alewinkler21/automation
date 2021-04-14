import React, { Component } from "react";
import PropTypes from "prop-types";

class DeleteVideo extends Component {
	static propTypes = {
		identifier: PropTypes.string.isRequired,
		description: PropTypes.string.isRequired,
		cancel: PropTypes.func.isRequired,
		confirm: PropTypes.func.isRequired
	};
	state = {
			identifier: this.props.identifier,
			description: this.props.description
			};

	deleteMedia = () => {
		var url = 'deletemedia/';
		
		const value = '; ' + document.cookie;
		const parts = value.split('; ' + 'csrftoken' + '=');
		
		if (parts.length == 2) {
			var csrftoken = parts.pop().split(";").shift();
		}
		
		fetch(url, {
			method: 'POST',
			body: JSON.stringify(this.state.identifier),
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
				this.props.confirm();
			}
		});	
	}
	  
	render() {
		return <div className="modal is-active">
				<div className="modal-background" />
					<div className="modal-card">
					<header className="modal-card-head">
						<p className="modal-card-title">
						Eliminar archivos
						</p>
						<button className="delete" onClick={() => this.props.cancel()} />
					</header>
					<section className="modal-card-body">
						<div className="content has-text-black">
							<p>
								{this.state.description}
							</p>
						</div>
					</section>
					<footer className="modal-card-foot">
						<button className="button" onClick={() => this.props.cancel()} >
						Cancelar
						</button>
						<button className="button is-danger" onClick={() => this.deleteMedia()}>
						Borrar
						</button>
					</footer>
					</div>
				</div>;
	}
}
export default DeleteVideo;