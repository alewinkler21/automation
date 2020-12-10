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
	  if (!this.state.data || this.state.data.length == 0) {
		  return (<div className="column">No hay archivos multimedia</div>);
	  }	  
	  return (<div className="column has-text-centered">  
	  {this.state.data.map(el => {
			var extension = el.split('.').pop();
			if (extension == 'jpg'){
				return <figure class="image is-5by3" key={el}>
						<a href={"camera/" + el} target="_blank">
							<img src={"camera/" + el}/>
						</a>
						</figure>;
			} else {
				return <figure class="image" key={el}>
						<video controls>
							<source src={"camera/" + el} type="video/mp4" />
						</video>
						</figure>;
			}
	  })}
	  </div>);
  }
}
export default Camera;