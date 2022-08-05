import React, { Component } from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import Actions from "./Actions";
import Camera from "./Camera";
import ActionsHistory from "./ActionsHistory";

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
	
    playmusic() {
		var url = 'playmusic/';
		
		var data = '';

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
				console.info(response);
			}
		});
	}
	
	toggleAlarm() {
		var url = 'togglealarm/';
		
		var data = {armed: !this.state.alarmArmed, useCamera: true, fired: false, detectPeople: true};

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
		fetch("alarm/").then(res => {
			if (res.ok) 
				return res.json();
			else
				throw new Error(res.status + ' ' + res.statusText);
			}).catch(error => console.error('Error:', error)).then(response => {
				if(response) {
					this.setState({alarmArmed: response.armed})
				}
			});
		fetch("systemstatus/").then(res => {
			if (res.ok) 
				return res.json();
			else
				throw new Error(res.status + ' ' + res.statusText);
			}).catch(error => console.error('Error:', error)).then(response => {
				if(response) {
					this.setState({systemStatus: response})
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
				return res.json();
			else
				throw new Error(res.status + ' ' + res.statusText);})
		.catch(error => console.error('Error:', error))
		.then(response => {
			if(response) {
				alert(response);
			}
		});
  	}

	componentDidMount() {
		this.fetchData();
		this.intervalID = setInterval(() => this.fetchData(), 5000);
	}
    
    componentWillUnmount(){
      clearInterval(this.intervalID);
    }
  
	render() {
		var content;
		switch(this.state.screen) {
			case "controls":
				content = <DataProvider
				endpoint="actions/" 
				render={data => <Actions data={data} />} />;
				break;
			case "system_status":
				var uptime = (this.state.systemStatus ? this.state.systemStatus.uptime : "");
				var temperature = (this.state.systemStatus ? this.state.systemStatus.temperature : "");
				var isDark = (this.state.systemStatus ? (this.state.systemStatus.isDark ? "está oscuro" : "está iluminado") : "");
				content = <div>
							<div class="field">
								<label class="label has-text-white">Timpo encendido</label>
								<span>{uptime}</span>
						  	</div>
							<div class="field">
								<label class="label has-text-white">Temperatura CPU</label>
								<span>{temperature}</span>
						  	</div>
							<div class="field">
								<label class="label has-text-white">Ambiente</label>
								<span>{isDark}</span>
						  	</div>
						  </div>;
				break;
			case "actions_history":
				content = <DataProvider
				endpoint="actionshistory/" 
				render={data => <ActionsHistory data={data} />} />;
				break;
			case "camera":
				content = <Camera />;
				break;
			default:
				content = <p><a href="/admin">Configuración</a></p>;
		}
		return (
			<div className="column has-text-centered">
				<nav className="navbar-menu is-active is-mobile">
					<div className="navbar-start">
						<button className="button is-large is-dark" href="#" onClick={() => this.navigate("controls")}>
							<span className="icon is-medium"> 
								<i className="fas fa-lg fa-lightbulb"></i>
							</span> 
						</button>
						<button className="button is-large is-dark" href="#" onClick={() => this.navigate("system_status")}>
							<span className="icon is-medium"> 
								<i className="fas fa-lg fa-heartbeat"></i>
							</span>
						</button>
						<button className="button is-large is-dark" href="#" onClick={() => this.navigate("actions_history")}>
							<span className="icon is-medium"> 
								<i className="fas fa-lg fa-history"></i>
							</span>
						</button>
						{
						//<button className="button is-large is-dark" href="#" onClick={() => this.navigate("camera")}>
						//	<span className="icon is-medium"> 
						//		<i className="fas fa-lg fa-file-video"></i>
						//	</span> 
						//</button>
						//<button className={this.state.alarmArmed ? "button is-large is-danger" : "button is-large is-dark"} href="#" onClick={() => this.playmusic()}>
						//	<span className="icon is-medium"> 
						//		<i className="fas fa-lg fa-music"></i> 
						//	</span> 
						//</button>
						}
						<button className="button is-large is-dark" href="#" onClick={() => window.location.href = "/admin"}>
						<span className="icon is-medium"> 
							<i className="fas fa-lg fa-cog"></i>
						</span> 
					</button>
					</div>
				</nav>
				{content}
			</div>)
	}
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App screen="controls" />, wrapper) : null;