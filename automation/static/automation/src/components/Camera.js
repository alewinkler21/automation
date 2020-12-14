import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";

class Camera extends Component {
  static propTypes = {
	  data: PropTypes.array.isRequired
  };
  state = {
		  data: this.props.data,
		  popupVisible: false,
		  popupFile: "",
		  popupTitle: "",
		  deleteVisible: false,
		  deleteIdentifier: "",
		  deleteDescription: ""
		  };
  
  componentDidUpdate() {
	  if (this.state.data !== this.props.data) {
		  this.setState({data: this.props.data});
	  }
  }
  
  render() {
	if (!this.state.data || this.state.data.length == 0) {
		return (<div className="has-text-centered">No hay archivos multimedia</div>);
	}
	// check if data is right for this rendering
	let sample = this.state.data[0];
	if (!sample.fileName) {  
		return "";
	}
	let dateFormat = {year: 'numeric', month: 'numeric', day: 'numeric', 
					  hour: 'numeric', minute: 'numeric', second: 'numeric', 
					  hour12: false, weekday: 'long'};
	let popupContent;
	if (this.state.popupVisible) {
			popupContent = <div className="modal is-active">
				<div className="modal-background" />
				<div className="modal-card">
				<header className="modal-card-head">
					<p className="modal-card-title">{this.state.popupTitle}</p>
					<button className="delete" onClick={() => this.setState({popupVisible: false, popupFile: "", popupTitle: ""})} />
				</header>
				<section className="modal-card-body">
					<div className="content">
						<video width="720" height="480" controls>
							<source src={"camera/" + this.state.popupFile} type="video/mp4" />
						</video>
					</div>
				</section>
				</div>
			</div>;
	} else if (this.state.deleteVisible) {
			popupContent = <div className="modal is-active">
				<div className="modal-background" />
				<div className="modal-card">
				<header className="modal-card-head">
					<p className="modal-card-title">Eliminar archivos</p>
					<button className="delete" onClick={() => this.setState({
						deleteVisible: false, 
						deleteIdentifier: "", 
						deleteDescription: ""})} />
				</header>
				<section className="modal-card-body">
					<div className="content">
						<p>
							{this.state.deleteDescription}
						</p>
					</div>
				</section>
				<footer className="modal-card-foot">
					<button className="button" onClick={() => this.setState({
						deleteVisible: false, 
						deleteIdentifier: "", 
						deleteDescription: ""})} >Cancelar</button>
					<button className="button is-danger" onClick={() => this.setState({
						deleteVisible: false, 
						deleteIdentifier: "", 
						deleteDescription: ""})}>Borrar</button>
				</footer>
				</div>
			</div>;
	}
	return <div>
			{popupContent}
			<ul className="has-text-centered">  
			{this.state.data.map(el => (
			  <li key={el.id} className="notification">
				<div className="columns is-mobile">
					<div className="column">
						<a className={el.triggeredByAlarm ? "" : "has-text-info"}
							href="#" onClick={() => this.setState({
							popupVisible: true, 
							popupFile: el.fileName,
							popupTitle: new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(el.dateCreated))})}>
						{new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(el.dateCreated))}	
						</a>
					</div>
					<div className="column is-1">
						<a className="delete is-medium" href="#" onClick={() => this.setState({
							deleteVisible: true, 
							deleteIdentifier: el.identifier,
							deleteDescription: new Intl.DateTimeFormat("es-ES", dateFormat).format(Date.parse(el.dateCreated))})}></a>
					</div>
				</div>
	  		  </li>
	  		  ))}
	  		</ul>
		</div>;
  }
}
export default Camera;