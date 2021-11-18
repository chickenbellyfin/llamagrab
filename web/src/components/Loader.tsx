import { LoadingOutlined } from "@ant-design/icons"
import { Col, Row, Spin } from "antd"
import React from "react"

type LoaderArgs<Props, ResultType> = {
  loaderFunc: (props: Props) => Promise<ResultType>
  componentBuilder: (
    result: ResultType,
    props: Props,
    invalidate: () => void
  ) => JSX.Element
}

type LoaderState<T> = {
  isLoading: boolean,
  firstLoad: boolean
  result?: T
}

export default function Loader<Props, ResultType>({loaderFunc, componentBuilder}: LoaderArgs<Props, ResultType>) {

  return class extends React.Component<Props, LoaderState<ResultType>> {

    constructor(props: Props) {
      super(props);
      this.state = {
        isLoading: true,
        firstLoad: true
      }
    }
    
    componentDidMount() {
      this.load()
    }

    load = () => {
      loaderFunc(this.props).then(result => {
        if(result){
          this.setState({
            isLoading: false,
            result: result,
            firstLoad: false
          })
        }
      })
      .catch(() => {}) // todo
    }

    onInvalidate = () => {
      this.setState({
        isLoading: true
      }, this.load)
    }

    render() {
      return (
      <>
        {this.state.firstLoad && 
          <Row justify='center' style={{padding:'20px'}}>
            <Col>
              <Spin indicator={
                <LoadingOutlined style={{fontSize: 48}}/>}/>
            </Col>
          </Row>
        }
        {!this.state.firstLoad && this.state.result &&
          <Spin spinning={this.state.isLoading} indicator={<div/>}>
            {componentBuilder(this.state.result, this.props, this.onInvalidate)}
          </Spin>
        }  
      </>);
    }
  };
}