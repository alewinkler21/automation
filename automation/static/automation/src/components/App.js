import React, { Component } from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import Buttons from "./Buttons";
import History from "./History";

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
    
	render() {
		console.log(this.state.screen);
		switch(this.state.screen) {
			case "main":
				return (<div className="has-text-centered">
				<ul>
					<li><a href="/admin">Configuración</a></li>
					<li><a href="#" onClick={() => this.navigate("history")}>Historia</a></li>
				</ul>
				<DataProvider
				endpoint="gpiodevices/" 
				render={data => <Buttons data={data} />} />
				</div>);
			case "history":
				return (<div className="has-text-centered">
				<ul>
					<li><a href="/admin">Configuración</a></li>
					<li><a href="#" onClick={() => this.navigate("main")}>Principal</a></li>
				</ul>
				<DataProvider
				endpoint="gpiodevices/" 
				render={data => <History data={data} />} />
				</div>);
			default:
				return (<div className="has-text-centered">
				<p><a href="/admin">Configuración</a></p>
				</div>);
			
		}
	}
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App screen="main" />, wrapper) : null;