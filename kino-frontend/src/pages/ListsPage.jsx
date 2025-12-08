import React, { useEffect, useState } from 'react';
import { getCurrentUser, getUserLists, createList } from '../api';
import '../auth.css';

const ListsPage = () => {
  const [me, setMe] = useState(null);
  const [lists, setLists] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  const fetchLists = async (userId) => {
    const resp = await getUserLists(userId);
    setLists(resp.data || []);
  };

  useEffect(() => {
    getCurrentUser()
      .then((resp) => {
        setMe(resp.data);
        return fetchLists(resp.data.id);
      })
      .catch(() => {
        setError('Нужен вход для работы со списками');
      });
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await createList({ title, description });
      setTitle('');
      setDescription('');
      if (me) await fetchLists(me.id);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось создать список';
      setError(msg);
    }
  };

  return (
    <main>
      <div className="page-container" style={{flexDirection:'column', background:'linear-gradient(135deg,#18181b 0%,#0f0f12 100%)'}}>
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', gap:'16px', flexWrap:'wrap'}}>
          <div>
            <h1 style={{marginBottom:'8px'}}>Мои списки</h1>
            <p style={{color:'#9aa0b5'}}>Создавайте подборки, добавляйте фильмы и делитесь ими.</p>
          </div>
          <form onSubmit={handleCreate} style={{display:'grid', gap:'8px', minWidth:'280px', background:'#0f0f12', border:'1px solid #25252c', borderRadius:'12px', padding:'12px'}}>
            <input placeholder="Название списка" value={title} onChange={(e)=>setTitle(e.target.value)} required />
            <textarea placeholder="Описание (опционально)" value={description} onChange={(e)=>setDescription(e.target.value)} rows={2}/>
            <button type="submit" className="btn-watch-later" style={{background:'linear-gradient(135deg,#6ab4ff,#5f8bff)', color:'#0f0f10', fontWeight:600}}>Создать список</button>
          </form>
        </div>

        {error && <p style={{color:'red', marginTop:'12px'}}>{error}</p>}

        <div style={{marginTop:'24px'}}>
          {lists.length === 0 && <p style={{color:'#aaa'}}>Списков нет</p>}
          <ul style={{listStyle:'none', padding:0, display:'grid', gap:'16px', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))'}}>
            {lists.map((lst)=>(
              <li key={lst.id} style={{padding:'16px', border:'1px solid #25252c', borderRadius:'12px', background:'#0f0f12', boxShadow:'0 8px 18px rgba(0,0,0,0.25)'}}>
                <h3 style={{marginBottom:'6px'}}>{lst.title}</h3>
                {lst.description && <p style={{color:'#cfd3e0', marginBottom:'8px'}}>{lst.description}</p>}
                <p style={{color:'#9aa0b5'}}>Фильмов: {lst.movie_count ?? 0}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
};

export default ListsPage;
