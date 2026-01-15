import { useEffect, useState } from "react";
import api from "../api/axios";

export default function Dashboard() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    api.get("/events")
      .then(res => setEvents(res.data))
      .catch(() => alert("Not authorized"));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      {events.map(event => (
        <div
          key={event.id}
          className="border p-4 mb-3 rounded"
        >
          <h2 className="font-semibold">{event.title}</h2>
          <p>Status: {event.status}</p>
          <p>Date: {event.date}</p>
        </div>
      ))}
    </div>
  );
}
