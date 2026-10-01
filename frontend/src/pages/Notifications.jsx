import {useEffect,useState} from 'react';
import {Bell,Check} from 'lucide-react';
import api from '../services/api';

export default function Notifications(){
  const [items,setItems]=useState([]);
  const load=async()=>{
  const r=await api.get('/api/notifications');
  setItems(r.data);
};

useEffect(()=>{
  load();
},[]);
  const read=async(id)=>{
  await api.put(`/api/notifications/${id}/read`);
  await load();
};
  return <div className="page"><div className="section-head"><div><p className="eyebrow">UPDATES</p><h1>Notifications</h1><p className="muted">RSVP confirmations, announcements, cancellations and waitlist updates.</p></div></div><section className="panel notification-list">{items.length?items.map(n=><div className={`notification ${n.read?'read':''}`} key={n.id}><div className="notification-icon"><Bell size={17}/></div><div className="notification-body"><b>{n.type.replaceAll('_',' ')}</b><p>{n.message}</p><small>{new Date(n.created_at).toLocaleString()}</small></div>{!n.read&&<button className="iconbtn" title="Mark as read" onClick={()=>read(n.id)}><Check size={16}/></button>}</div>):<p className="muted">No notifications yet.</p>}</section></div>
}
