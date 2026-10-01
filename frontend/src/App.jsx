import {useState} from 'react';
import {LayoutDashboard,CalendarDays,Bell} from 'lucide-react';
import {useAuth} from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Notifications from './pages/Notifications';
import Nav from './components/Nav';

export default function App(){
 const {user,loading}=useAuth(); const [view,setView]=useState('dashboard');
 if(loading)return <div className="loading">Loading CloudEvents…</div>;
 if(!user)return <Login/>;
 return <div className="app"><Nav/><aside className="sidebar"><button className={view==='dashboard'?'active':''} onClick={()=>setView('dashboard')}><LayoutDashboard/> Dashboard</button><button className={view==='events'?'active':''} onClick={()=>setView('events')}><CalendarDays/> Events</button><button className={view==='notifications'?'active':''} onClick={()=>setView('notifications')}><Bell/> Notifications</button><div className="side-note"><b>Cloud proof</b><span>PostgreSQL · JWT · REST · WebSocket</span></div></aside><main className="content">{view==='dashboard'?<Dashboard/>:view==='events'?<Events/>:<Notifications/>}</main></div>
}
