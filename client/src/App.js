import React, {useState} from 'react';
import Terminal, {LineType} from 'react-terminal-ui';
import './App.css';
import Auth from './Auth';

let ws = null;

const App = (props = {}) => {
    const [statusData, setStatusData] = useState({enabled: false});
    const [terminalLineData] = useState([
        {type: LineType.Output, value: 'Welcome to the React Terminal UI Demo!'},
        {type: LineType.Input, value: 'Some previous input received'},
    ]);

    const [isAuth, setIsAuth] = useState(false);

    const sendData = data => {
        ws.send(JSON.stringify(data));
    };
    const exec = command => {
        terminalLineData.push({type: LineType.Input, value: <div className="red">{command}</div>});
        if (command) {
            sendData({action: 'exec', command});
        }
    }

    const auth = (socketAddress, login, password) => {
        try {
            ws.close();
            ws = null;
        } catch (e) {
        }
        ws = new WebSocket(`ws://${socketAddress}`);
        ws.onerror = function (e) {
            console.error(e);
            alert('Something wrong...');
            setIsAuth(false);
        }

        ws.onopen = function (e) {
            sendData({login, password});
            terminalLineData.push({type: LineType.Output, value: 'The connection is established.'});
        };

        ws.onclose = function (e) {
            terminalLineData.push({type: LineType.Output, value: 'Connection lost.'});
            setIsAuth(false);
        };

        ws.onmessage = function (e) {
            const {status, action, result} = JSON.parse(e.data);
            if (action === 'log_message') {
                terminalLineData.push({type: LineType.Output, value: result});
            } else if (action === 'exec') {
                terminalLineData.push({type: LineType.Input, value: result});
            } else if (action === 'status_message') {
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
                    statusData.enabled
                        ? <div className="info-line">
                            <div className="with-point online status">Server online</div>
                            <div>
                                <div>{statusData.players.online} / {statusData.players.max} players</div>
                                <div className="with-delimiter">{statusData.brand} {statusData.version}</div>
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
