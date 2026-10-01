import {useEffect,useState} from 'react'; import {CalendarDays,MapPin,Users,Clock} from 'lucide-react'; import api from '../services/api'; import {useAuth} from '../context/AuthContext';
export default function Events(){const {user}=useAuth();const [events,setEvents]=useState([]);const [selected,setSelected]=useState(null);const [status,setStatus]=useState('');
const load=async()=>{
  const r=await api.get('/api/events');
  setEvents(r.data);
};

useEffect(()=>{
  load();
},[]);
const rsvp=async(s)=>{try{await api.post(`/api/events/${selected.id}/rsvp`,{status:s});setStatus(`Your RSVP is ${s.replace('_',' ')}.`)}catch(e){setStatus(e.response?.data?.detail||'Unable to update RSVP')}};return <><Navless/><div className="page"><div className="section-head"><div><p className="eyebrow">EVENT DISCOVERY</p><h1>Upcoming events</h1><p className="muted">Browse published events and respond in real time.</p></div>{user?.role!=='ATTENDEE'&&<span className="badge">Organizer mode</span>}</div><div className="event-grid">{events.map(e=><article className="event-card" key={e.id} onClick={()=>{setSelected(e);setStatus('')}}><div className="event-top"><span className="tag">{e.event_type}</span><span className={`status ${e.status.toLowerCase()}`}>{e.status}</span></div><h2>{e.event_name}</h2><p>{e.description}</p><div className="meta"><span><CalendarDays size={15}/>{e.event_date}</span><span><Clock size={15}/>{e.start_time.slice(0,5)}</span><span><MapPin size={15}/>{e.venue}</span><span><Users size={15}/>Cap {e.maximum_capacity}</span></div></article>)}</div>{selected&&<div className="modal-bg" onClick={()=>setSelected(null)}><div className="modal" onClick={e=>e.stopPropagation()}><button className="close" onClick={()=>setSelected(null)}>×</button><span className="tag">{selected.event_type}</span><h2>{selected.event_name}</h2><p>{selected.description}</p><div className="details"><b>{selected.event_date}</b><span>{selected.start_time.slice(0,5)}–{selected.end_time.slice(0,5)}</span><span>{selected.venue}</span></div>{user?.role==='ATTENDEE'&&<><h3>Your response</h3><div className="rsvp-row"><button onClick={()=>rsvp('GOING')}>Going</button><button onClick={()=>rsvp('MAYBE')}>Maybe</button><button onClick={()=>rsvp('NOT_GOING')}>Not Going</button></div></>}{status&&<div className="success">{status}</div>}</div></div>}</div></>}
function Navless(){return null}
