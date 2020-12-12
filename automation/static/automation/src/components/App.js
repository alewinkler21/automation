import React, { Component } from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import Buttons from "./Buttons";
import Camera from "./Camera";

class App extends Component {	

	static propTypes = {
		screen: PropTypes.string.isRequired
	};
	
	state = {
		screen: this.props.screen,
		alarmArmed: false
	};
	
    navigate = (screen) => {
    	this.setState({screen: screen});
    };
	
	toggleAlarm() {
		var url = 'togglealarm/';
		
		var data = {armed: !this.state.alarmArmed, useCamera: true};

		const value = '; ' + document.cookie;
		const parts = value.split('; ' + 'csrftoken' + '=');
		
		if (parts.length == 2) {
			var csrftoken = parts.pop().split(";").shift();
		}
		
		fetch(url, {
			method: 'POST',
			body: JSON.stringify(data),
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
				this.setState({alarmArmed: response.armed})
			}
		});
	}

	fetchData(){
		fetch("getalarm/").then(res => {
			if (res.ok) 
				return res.json();
			else
				throw new Error(res.status + ' ' + res.statusText);
			}).catch(error => console.error('Error:', error)).then(response => {
				if(response) {
					this.setState({alarmArmed: response.armed})
				}
			});	  
	}

	recordVideo(){
		const value = '; ' + document.cookie;
		const parts = value.split('; ' + 'csrftoken' + '=');
		
		if (parts.length == 2) {
			var csrftoken = parts.pop().split(";").shift();
		}
		fetch("recordvideo/", {
			method: 'POST',
			headers:{
				'Content-Type': 'application/json',
				'X-CSRFToken': csrftoken
			}
		}).then(res => {
			if (res.ok) 
				return res;
			else
				throw new Error(res.status + ' ' + res.statusText);})
		.catch(error => console.error('Error:', error))
		.then(response => {
			if(response) {
				console.log(response);
			}
		});
  	}

	componentDidMount() {
		this.fetchData();
	}

	render() {
		let content;
		switch(this.state.screen) {
			case "controls":
				content = <DataProvider
				endpoint="relays/" 
				render={data => <Buttons data={data} />} />;
				break;
			case "camera":
				content = <DataProvider
				endpoint="getmedia/" 
				render={data => <Camera data={data} />} />;
				break;
			default:
				content = <p><a href="/admin">Configuración</a></p>;
		}
		return (
			<div className="column has-text-centered">
				<nav className="navbar-menu is-active is-mobile">
					<div className="navbar-start">
						<button className={this.state.alarmArmed ? "button is-danger" : "button"} href="#" onClick={() => this.toggleAlarm()}>Alarma</button>
						<button className="button" href="#" onClick={() => this.recordVideo()}>Grabar Video</button>
					</div>
				</nav>
				<nav className="navbar-menu is-active">
					<div className="navbar-start">
						<a className="navbar-item" href="#" onClick={() => this.navigate("controls")}>Controles</a>
						<a className="navbar-item" href="#" onClick={() => this.navigate("camera")}>Cámara</a>
						<a className="navbar-item" href="/admin" >Configuración</a>
					</div>
				</nav>
				{content}
			</div>)
	}
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App screen="controls" />, wrapper) : null;