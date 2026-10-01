
import {useEffect,useState} from 'react';
import api from '../services/api';
import {useAuth} from '../context/AuthContext';
import StatCard from '../components/StatCard';
import {Activity,Plus,Send,Pencil,Trash2,XCircle} from 'lucide-react';

const blank={
  event_name:'',
  description:'',
  event_type:'Workshop',
  event_date:'',
  start_time:'10:00',
  end_time:'13:00',
  venue:'Innovation Hall',
  online_link:'',
  maximum_capacity:100,
  registration_deadline:''
};

export default function Dashboard(){
  const {user}=useAuth();
  const [events,setEvents]=useState([]);
  const [selected,setSelected]=useState(null);
  const [analytics,setAnalytics]=useState(null);
  const [editing,setEditing]=useState(false);
  const [form,setForm]=useState(blank);
  const [announcement,setAnnouncement]=useState({title:'',message:''});
  const [message,setMessage]=useState('');

  const load=async()=>{
    const r=await api.get('/api/events');
    setEvents(r.data);
  };

  useEffect(()=>{
    load();
  },[]);

  const pick=async(e)=>{
    setSelected(e);
    setEditing(false);
    setMessage('');

    try{
      const r=await api.get(`/api/events/${e.id}/analytics`);
      setAnalytics(r.data);
    }catch{
      setAnalytics(null);
    }
  };

  useEffect(()=>{
    if(!selected)return;

    const ws=new WebSocket(
      `${api.defaults.baseURL.replace(/^http/,'ws')}/ws/events/${selected.id}`
    );

    ws.onmessage=msg=>{
      const p=JSON.parse(msg.data);
      if(p.analytics)setAnalytics(p.analytics);
    };

    return()=>ws.close();
  },[selected]);

  const create=async ev=>{
    ev.preventDefault();

    try{
      await api.post('/api/events',{
        ...form,
        maximum_capacity:Number(form.maximum_capacity),
        registration_deadline:new Date(form.registration_deadline).toISOString()
      });

      setForm(blank);
      setMessage('Event published.');
      load();
    }catch(e){
      setMessage(e.response?.data?.detail||'Could not create event');
    }
  };

  const edit=()=>{
    setForm({
      ...selected,
      registration_deadline:new Date(
        selected.registration_deadline
      ).toISOString().slice(0,16)
    });

    setEditing(true);
    setMessage('');
  };

  const update=async ev=>{
    ev.preventDefault();

    try{
      await api.put(`/api/events/${selected.id}`,{
        ...form,
        maximum_capacity:Number(form.maximum_capacity),
        registration_deadline:new Date(
          form.registration_deadline
        ).toISOString()
      });

      setMessage('Event updated.');
      setEditing(false);

      await load();

      const fresh=(
        await api.get(`/api/events/${selected.id}`)
      ).data;

      setSelected(fresh);
    }catch(e){
      setMessage(
        e.response?.data?.detail||'Could not update event'
      );
    }
  };

  const cancel=async()=>{
    if(!confirm('Cancel this event?'))return;

    try{
      await api.post(`/api/events/${selected.id}/cancel`);
      setMessage('Event cancelled.');
      load();
    }catch(e){
      setMessage(
        e.response?.data?.detail||'Could not cancel event'
      );
    }
  };

  const remove=async()=>{
    if(!confirm('Permanently delete this event?'))return;

    try{
      await api.delete(`/api/events/${selected.id}`);
      setSelected(null);
      setAnalytics(null);
      load();
    }catch(e){
      setMessage(
        e.response?.data?.detail||'Could not delete event'
      );
    }
  };

  const send=async ev=>{
    ev.preventDefault();

    try{
      await api.post(
        `/api/events/${selected.id}/announcements`,
        announcement
      );

      setAnnouncement({title:'',message:''});
      setMessage(
        'Announcement published and notifications generated.'
      );
    }catch(e){
      setMessage(
        e.response?.data?.detail||'Could not publish announcement'
      );
    }
  };

  if(user?.role==='ATTENDEE')return <AttendeeView/>;

  return (
    <div className="page">

      <div className="section-head">
        <div>
          <p className="eyebrow">ORGANIZER CONSOLE</p>
          <h1>Operations dashboard</h1>
          <p className="muted">
            Live event health, capacity and attendee response.
          </p>
        </div>

        <div className="live">
          <Activity size={16}/> LIVE
        </div>
      </div>

      <div className="stats">
        <StatCard
          label="Total Events"
          value={events.length}
        />

        <StatCard
          label="Upcoming"
          value={
            events.filter(
              e=>['PUBLISHED','FULL'].includes(e.status)
            ).length
          }
        />

        <StatCard
          label="Going"
          value={analytics?.going??0}
        />

        <StatCard
          label="Maybe"
          value={analytics?.maybe??0}
        />

        <StatCard
          label="Available Seats"
          value={analytics?.available_seats??0}
        />
      </div>

      <div className="two-col">

        <section className="panel">

          <h2>
            <Plus size={18}/>
            {editing?'Edit event':'Create event'}
          </h2>

          <form
            className="form-grid"
            onSubmit={editing?update:create}
          >

            <div className="form-field">
              <label htmlFor="event_name">
                Event Name
              </label>

              <input
                id="event_name"
                required
                placeholder="e.g. Cloud Computing Workshop"
                type="text"
                value={form.event_name||''}
                onChange={e=>
                  setForm({
                    ...form,
                    event_name:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="event_type">
                Event Type
              </label>

              <input
                id="event_type"
                required
                placeholder="e.g. Workshop"
                type="text"
                value={form.event_type||''}
                onChange={e=>
                  setForm({
                    ...form,
                    event_type:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="event_date">
                Event Date
              </label>

              <input
                id="event_date"
                required
                type="date"
                value={form.event_date||''}
                onChange={e=>
                  setForm({
                    ...form,
                    event_date:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="start_time">
                Start Time
              </label>

              <input
                id="start_time"
                required
                type="time"
                value={form.start_time||''}
                onChange={e=>
                  setForm({
                    ...form,
                    start_time:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="end_time">
                End Time
              </label>

              <input
                id="end_time"
                required
                type="time"
                value={form.end_time||''}
                onChange={e=>
                  setForm({
                    ...form,
                    end_time:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="venue">
                Venue
              </label>

              <input
                id="venue"
                required
                placeholder="e.g. Innovation Hall"
                type="text"
                value={form.venue||''}
                onChange={e=>
                  setForm({
                    ...form,
                    venue:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="maximum_capacity">
                Maximum Capacity
              </label>

              <input
                id="maximum_capacity"
                required
                min="1"
                placeholder="e.g. 100"
                type="number"
                value={form.maximum_capacity||''}
                onChange={e=>
                  setForm({
                    ...form,
                    maximum_capacity:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field">
              <label htmlFor="registration_deadline">
                Registration Deadline
              </label>

              <input
                id="registration_deadline"
                required
                type="datetime-local"
                value={form.registration_deadline||''}
                onChange={e=>
                  setForm({
                    ...form,
                    registration_deadline:e.target.value
                  })
                }
              />
            </div>

            <div className="form-field full-width">
              <label htmlFor="description">
                Description
              </label>

              <textarea
                id="description"
                required
                placeholder="Describe the event..."
                value={form.description||''}
                onChange={e=>
                  setForm({
                    ...form,
                    description:e.target.value
                  })
                }
              />
            </div>

            <div className="button-row">
              <button className="primary">
                {editing?'Save changes':'Publish event'}
              </button>

              {editing&&(
                <button
                  type="button"
                  className="ghost"
                  onClick={()=>setEditing(false)}
                >
                  Cancel edit
                </button>
              )}
            </div>

          </form>

          {message&&(
            <div className="success">
              {message}
            </div>
          )}

        </section>

        <section className="panel">

          <h2>Your events</h2>

          {events.map(e=>(
            <button
              className={`event-row ${
                selected?.id===e.id?'selected':''
              }`}
              key={e.id}
              onClick={()=>pick(e)}
            >
              <span>
                <b>{e.event_name}</b>
                <small>
                  {e.event_date} · {e.status}
                </small>
              </span>

              <span>→</span>
            </button>
          ))}

        </section>

      </div>

      {selected&&(
        <section className="panel analytics">

          <div className="section-head compact">

            <div>
              <h2>
                Live analytics · {selected.event_name}
              </h2>

              <p className="muted">
                WebSocket updates are pushed to this screen
                after committed RSVP changes.
              </p>
            </div>

            <div className="button-row">

              <button
                className="iconbtn"
                title="Edit"
                onClick={edit}
              >
                <Pencil size={16}/>
              </button>

              <button
                className="iconbtn"
                title="Cancel event"
                onClick={cancel}
              >
                <XCircle size={16}/>
              </button>

              <button
                className="iconbtn"
                title="Delete event"
                onClick={remove}
              >
                <Trash2 size={16}/>
              </button>

            </div>

          </div>

          <div className="analytics-grid">

            <div>
              <strong>{analytics?.going??0}</strong>
              <span>Going</span>
            </div>

            <div>
              <strong>{analytics?.maybe??0}</strong>
              <span>Maybe</span>
            </div>

            <div>
              <strong>{analytics?.not_going??0}</strong>
              <span>Not Going</span>
            </div>

            <div>
              <strong>{analytics?.waitlisted??0}</strong>
              <span>Waitlist</span>
            </div>

            <div>
              <strong>
                {analytics?.response_rate??0}%
              </strong>
              <span>Response rate</span>
            </div>

            <div>
              <strong>
                {analytics?.capacity_utilization??0}%
              </strong>
              <span>Capacity used</span>
            </div>

          </div>

          <div className="announcement">

            <h3>
              <Send size={16}/>
              Announcement
            </h3>

            <form onSubmit={send}>

              <label htmlFor="announcement_title">
                Announcement Title
              </label>

              <input
                id="announcement_title"
                required
                placeholder="Enter announcement title"
                value={announcement.title}
                onChange={e=>
                  setAnnouncement({
                    ...announcement,
                    title:e.target.value
                  })
                }
              />

              <label htmlFor="announcement_message">
                Announcement Message
              </label>

              <textarea
                id="announcement_message"
                required
                placeholder="Enter announcement message"
                value={announcement.message}
                onChange={e=>
                  setAnnouncement({
                    ...announcement,
                    message:e.target.value
                  })
                }
              />

              <button className="primary">
                Publish announcement
              </button>

            </form>

          </div>

        </section>
      )}

    </div>
  );
}

function AttendeeView(){

  const [rsvps,setRsvps]=useState([]);

  useEffect(()=>{
    api.get('/api/rsvps/me')
      .then(r=>setRsvps(r.data));
  },[]);

  return (
    <div className="page">

      <div className="section-head">

        <div>
          <p className="eyebrow">ATTENDEE SPACE</p>
          <h1>My RSVPs</h1>
          <p className="muted">
            Your current event responses.
          </p>
        </div>

      </div>

      <div className="panel">

        <div className="rsvp-list">

          {rsvps.length
            ?rsvps.map(r=>(
              <div
                className="rsvp-item"
                key={r.id}
              >
                <b>Event #{r.event_id}</b>

                <span
                  className={`tag ${r.status.toLowerCase()}`}
                >
                  {r.status.replace('_',' ')}
                </span>
              </div>
            ))
            :(
              <p className="muted">
                No RSVPs yet. Open Events from the sidebar.
              </p>
            )
          }

        </div>

      </div>

    </div>
  );
}

