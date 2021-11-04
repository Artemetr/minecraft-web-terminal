import {useState} from 'react';
import './Auth.css';

const Auth = ({auth}) => {
    const [socketAddress, setSocketAddress] = useState(localStorage.getItem('mwtc-socketAddress') || '');
    const setLocalStorageSocketAddress = value => {
        localStorage.setItem('mwtc-socketAddress', value);
        setSocketAddress(value);
    };

    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');

    return (
        <form onSubmit={e => auth(socketAddress, login, password) || e.preventDefault()}>
            <div className="card card--inverted">
                <h2>Web Terminal</h2>
                <a href="https://github.com/Artemetr/minecraft-web-terminal">by artemetr</a>
                <label className="input">
                    <input className="input__field" type="text" placeholder=" " value={login} onChange={e => setLogin(e.target.value)}/>
                    <span className="input__label">Login</span>
                </label>

                <label className="input">
                    <input className="input__field" type="password" placeholder=" " value={password} onChange={e => setPassword(e.target.value)}/>
                    <span className="input__label">Password</span>
                </label>

                <label className="input">
                    <input className="input__field" type="text" placeholder=" " value={socketAddress} onChange={e => setLocalStorageSocketAddress(e.target.value)}/>
                    <span className="input__label">Server address</span>
                </label>

                <div className="button-group">
                    <button onClick={e => auth(socketAddress, login, password) || e.preventDefault()}>Sign in</button>
                </div>
            </div>
        </form>
    );
};

export default Auth;
