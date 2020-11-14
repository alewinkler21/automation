import React, { Component } from "react";
import { Chart } from "react-charts";
import PropTypes from "prop-types";
	  
class History extends Component {
  static propTypes = {
	  data: PropTypes.array.isRequired
  };
  state = {
		  data: this.props.data
		  };
    	
  render() {
	  const data = [
	      {
		        label: 'Series 1',
		        data: [[0, 1], [1, 0], [2, 1], [3, 1], [4, 0]]
		      }
		    ];
			 
			  const axes = [
			      { primary: true, type: 'ordinal', position: 'bottom' },
			      { type: 'linear', position: 'left' }
			    ];
			  
	  return (<div
			      style={{
			        width: '500px',
			        height: '200px'
			      }}>
	  <Chart data={data} axes={axes} />
			    </div>
			  )
  }
}
export default History;
