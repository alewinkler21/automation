import React, { Component } from "react";
import PropTypes from "prop-types";
import key from "weak-key";

class Camera extends Component {
  static propTypes = {
	  data: PropTypes.array.isRequired
  };
  state = {
		  data: this.props.data
		  };
  
  componentDidUpdate() {
	  if (this.state.data !== this.props.data) {
		  this.setState({data: this.props.data});
	  }
  }
  
  render() {
	  if (!this.state.data) {
		  return (<div className="column">No captured images</div>);
	  }	  
	  return (<div className="column has-text-centered">  
	  {this.state.data.map(el => {
			var extension = el.name.split('.').pop();
			if (extension == 'jpg'){
				return <figure class="image is-5by3" key={el.name}>
						<a href={"http://192.168.0.165/camera/" + el.name} target="_blank">
							<img src={"http://192.168.0.165/camera/" + el.name}/>
						</a>
					</figure>;
			} else {
				return <figure class="image" key={el.name}>
						<video width="360" height="240" controls>
							<source src={"http://192.168.0.165/camera/" + el.name} type="video/mp4" />
						</video>
						</figure>;
			}
	  })}
	  </div>);
  }
}
export default Camera;