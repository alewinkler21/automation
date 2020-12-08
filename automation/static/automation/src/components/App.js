import React, { Component } from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import Buttons from "./Buttons";
import History from "./History";
import Camera from "./Camera";

class App extends Component {	

	static propTypes = {
		screen: PropTypes.string.isRequired
	};
	
	state = {
		screen: this.props.screen
	};
	
    navigate = (screen) => {
    	this.setState({screen: screen});
    };
	
	toggleAlarm(status) {
		var url = 'togglealarm/';
		
		var data = {armed: !status, useCamera: true};

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
				el.armed = response.armed;
				// this.setState({data: this.state.data})
			}
		});
	}

	render() {
		switch(this.state.screen) {
			case "controls":
				return (<div className="has-text-centered">
				<ul>
					<li><a href="#" onClick={() => this.toggleAlarm(false)}>Alarma</a></li>
					<li><a href="#" onClick={() => this.navigate("controls")}>Controles</a></li>
					<li><a href="#" onClick={() => this.navigate("camera")}>Cámara</a></li>
					<li><a href="#" onClick={() => this.navigate("history")}>Historia</a></li>
					<li><a href="/admin">Configuración</a></li>	
				</ul>
				<DataProvider
				endpoint="relays/" 
				render={data => <Buttons data={data} />} />
				</div>);
			case "history":
				return (<div className="has-text-centered">
				<ul>
					<li><a href="#" onClick={() => this.toggleAlarm(false)}>Alarma</a></li>
					<li><a href="#" onClick={() => this.navigate("controls")}>Controles</a></li>
					<li><a href="#" onClick={() => this.navigate("camera")}>Cámara</a></li>
					<li><a href="#" onClick={() => this.navigate("history")}>Historia</a></li>
					<li><a href="/admin">Configuración</a></li>
				</ul>
				<DataProvider
				endpoint="history/" 
				render={data => <History data={data} />} />
				</div>);
			case "camera":
				return (<div className="has-text-centered">
				<ul>
					<li><a href="#" onClick={() => this.toggleAlarm(false)}>Alarma</a></li>
					<li><a href="#" onClick={() => this.navigate("controls")}>Controles</a></li>
					<li><a href="#" onClick={() => this.navigate("camera")}>Cámara</a></li>
					<li><a href="#" onClick={() => this.navigate("history")}>Historia</a></li>
					<li><a href="/admin">Configuración</a></li>
				</ul>
				<DataProvider
				endpoint="http://192.168.0.165/camera/" 
				render={data => <Camera data={data} />} />
				</div>);
			default:
				return (<div className="has-text-centered">
				<p><a href="/admin">Configuración</a></p>
				</div>);
			
		}
	}
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App screen="controls" />, wrapper) : null;