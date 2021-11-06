import React, {useState} from 'react';
import Terminal, {LineType} from 'react-terminal-ui';
import './App.css';
import Auth from './Auth';

let ws = null;

const App = (props = {}) => {
    const [statusData, setStatusData] = useState({status: false});
    const [terminalLineData] = useState([
        {type: LineType.Output, value: 'Welcome to the Web Terminal for Minecraft Server!'}
    ]);

    const [isAuth, setIsAuth] = useState(false);

    const sendData = data => {
        ws.send(JSON.stringify(data));
    };
    
    const exec = command => {
        terminalLineData.push({type: LineType.Input, value: <div className="log-message-input">{command}</div>});
        if (command) {
            sendData({action: 'exec', data: {command}});
        }
    }

    const auth = (socketAddress, login, password) => {
        try {
            ws.close();
            ws = null;
        } catch (e) {
        }
        ws = new WebSocket(`${socketAddress}`);
        ws.onerror = function (e) {
            console.error(e);
            alert('Something wrong...');
            setIsAuth(false);
        }

        ws.onopen = function (e) {
            sendData({action: 'auth', data: {login, password}});
            terminalLineData.push({type: LineType.Output, value: 'The connection is established'});
        };

        ws.onclose = function (e) {
            terminalLineData.push({type: LineType.Output, value: 'Connection lost'});
            setIsAuth(false);
        };

        ws.onmessage = function (e) {
            const {status, action, result, error} = JSON.parse(e.data);
            if (error) {
                console.error(error);
            }
            
            if (action === 'log_message') {
                const {message, type} = result;

                let value = null;
                let lineType = null;
                if (type === 'input') {
                    lineType = LineType.Input;
                    value = <div className="log-message-input">{message}</div>;
                } else if (type === 'output') {
                    lineType = LineType.Output;
                    value = <div className="log-message-output">{message}</div>;
                } else if (type === 'error') {
                    lineType = LineType.Output;
                    value = <div className="log-message-error">{message}</div>;
                } else if (type === 'warning') {
                    lineType = LineType.Output;
                    value = <div className="log-message-warning">{message}</div>;
                } else if (type === 'success') {
                    lineType = LineType.Output;
                    value = <div className="log-message-success">{message}</div>;
                } else {
                    console.error('Undefined type', type);
                    return;
                }
                
                terminalLineData.push({type: lineType, value});
            } else if (action === 'stats_message') {
                setStatusData(result);
            } else if (action === 'auth') {
                setIsAuth(!!status);
                if (!status) {
                    try {
                        ws.close();
                    } catch (e) {
                    }
                }
            }
        };
    };

    return (
        isAuth
            ? <div className="container">
                {
                    statusData.status
                        ? <div className="info-line">
                            <div className="with-point online status">Server online</div>
                            <div>
                                <div>{statusData.players.online} / {statusData.players.max} players</div>
                                <div className="with-delimiter">{statusData.version.name}</div>
                            </div>
                            <a href="https://github.com/Artemetr/minecraft-web-terminal">Developed by artemetr</a>
                        </div>
                        : <div className="info-line">
                            <div className="with-point offline">Server offline</div>
                            <a href="https://github.com/Artemetr/minecraft-web-terminal">Developed by artemetr</a>
                        </div>
                }
                <Terminal lineData={terminalLineData} onInput={terminalInput => exec(terminalInput)}/>
            </div>
            : <div className="container">
                <Auth auth={auth} />
            </div>
    )
};

export default App;
