import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getCurrentUser, getUserLists, createList } from '../api';
import { updateList, deleteList } from '../api';
import '../auth.css';

const ListsPage = () => {
  const [me, setMe] = useState(null);
  const [lists, setLists] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editIsPublic, setEditIsPublic] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const protectedTitles = ['буду смотреть', 'любимое', 'любимые', 'просмотренно', 'просмотрено', 'просмотренные'];

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
      await createList({ title, description, is_public: isPublic });
      setTitle('');
      setDescription('');
      setIsPublic(true);
      if (me) await fetchLists(me.id);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось создать список';
      setError(msg);
    }
  };

  const startEdit = (lst) => {
    setEditingId(lst.id);
    setEditTitle(lst.title);
    setEditDescription(lst.description || '');
    setEditIsPublic(lst.is_public !== false);
  };

  const saveEdit = async (listId) => {
    try {
      const resp = await updateList(listId, { title: editTitle, description: editDescription, is_public: editIsPublic });
      setLists((prev) => prev.map((l) => (l.id === listId ? resp.data : l)));
      setEditingId(null);
      setEditTitle('');
      setEditDescription('');
      setEditIsPublic(true);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось обновить список';
      setError(msg);
    }
  };

  const handleShare = async (listId) => {
    const url = `${window.location.origin}/lists/${listId}`;
    
    // Проверяем доступность Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(url);
        setCopiedId(listId);
        setTimeout(() => setCopiedId(null), 2000);
      } catch (err) {
        // Fallback на старый метод
        fallbackCopyTextToClipboard(url, listId);
      }
    } else {
      // Fallback на старый метод
      fallbackCopyTextToClipboard(url, listId);
    }
  };

  const fallbackCopyTextToClipboard = (text, listId) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        setCopiedId(listId);
        setTimeout(() => setCopiedId(null), 2000);
      } else {
        // Если и это не сработало, показываем URL в alert
        alert(`Ссылка на список:\n${text}`);
      }
    } catch (err) {
      // Если и это не сработало, показываем URL в alert
      alert(`Ссылка на список:\n${text}`);
    } finally {
      document.body.removeChild(textArea);
    }
  };

  const togglePublic = async (lst) => {
    try {
      const resp = await updateList(lst.id, { is_public: !lst.is_public });
      setLists((prev) => prev.map((l) => (l.id === lst.id ? resp.data : l)));
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось изменить видимость';
      setError(msg);
    }
  };

  const handleDelete = async (listId, titleVal) => {
    if (protectedTitles.includes(titleVal?.toLowerCase())) {
      setError('Этот список нельзя удалять');
      return;
    }
    try {
      await deleteList(listId);
      setLists((prev) => prev.filter((l) => l.id !== listId));
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось удалить список';
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
          <form onSubmit={handleCreate} className="review-form" style={{minWidth:'320px', background:'#0f0f12', border:'1px solid #2f2f37'}}>
            <h3 style={{color:'#f5f5f7'}}>Новый список</h3>
            <input placeholder="Название списка" value={title} onChange={(e)=>setTitle(e.target.value)} required />
            <textarea placeholder="Описание (опционально)" value={description} onChange={(e)=>setDescription(e.target.value)} rows={2}/>
            <label style={{display:'flex', alignItems:'center', gap:'8px', color:'#9aa0b5', cursor:'pointer'}}>
              <input type="checkbox" checked={!isPublic} onChange={(e)=>setIsPublic(!e.target.checked)} style={{width:'16px', height:'16px'}} />
              Сделать список приватным
            </label>
            <button type="submit" className="btn-watch-later" style={{background:'linear-gradient(135deg,#6ab4ff,#5f8bff)', color:'#0f0f10', fontWeight:600}}>Создать список</button>
          </form>
        </div>

        {error && <p style={{color:'red', marginTop:'12px'}}>{error}</p>}

        <div style={{marginTop:'24px'}}>
          {lists.length === 0 && <p style={{color:'#aaa'}}>Списков нет</p>}
          <ul style={{listStyle:'none', padding:0, display:'grid', gap:'16px', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))'}}>
            {lists.map((lst)=>(
              <li key={lst.id} style={{padding:'16px', border:'1px solid #25252c', borderRadius:'12px', background:'#0f0f12', boxShadow:'0 8px 18px rgba(0,0,0,0.25)'}}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', gap:'8px'}}>
                  <div style={{display:'flex', alignItems:'center', gap:'8px'}}>
                    <h3 style={{marginBottom:'0'}}>{lst.title}</h3>
                    {lst.is_public === false && <span title="Приватный список" style={{fontSize:'14px'}}>🔒</span>}
                  </div>
                  <div style={{display:'flex', gap:'4px'}}>
                    <button 
                      className="icon-button" 
                      title={lst.is_public ? "Сделать приватным" : "Сделать публичным"} 
                      onClick={()=>togglePublic(lst)}
                      style={{fontSize:'14px'}}
                    >
                      {lst.is_public ? '🌐' : '🔒'}
                    </button>
                    <button 
                      className="icon-button" 
                      title={copiedId === lst.id ? "Скопировано!" : "Поделиться"} 
                      onClick={()=>handleShare(lst.id)}
                      style={{fontSize:'14px'}}
                    >
                      {copiedId === lst.id ? '✓' : '🔗'}
                    </button>
                    {!protectedTitles.includes(lst.title?.toLowerCase()) && (
                      <button className="icon-button" title="Редактировать" onClick={()=>startEdit(lst)}>✎</button>
                    )}
                  </div>
                </div>
                {lst.description && <p style={{color:'#cfd3e0', marginBottom:'8px', marginTop:'6px'}}>{lst.description}</p>}
                <p style={{color:'#9aa0b5'}}>Фильмов: {lst.movie_count ?? 0}</p>
                <Link to={`/lists/${lst.id}`} style={{color:'#6ab4ff', marginTop:'8px', display:'inline-block'}}>Перейти к списку →</Link>

                {editingId === lst.id && (
                  <div className="review-form" style={{marginTop:'10px', background:'#0f0f12', border:'1px solid #2f2f37'}}>
                    <input value={editTitle} onChange={(e)=>setEditTitle(e.target.value)} />
                    <textarea rows={2} value={editDescription} onChange={(e)=>setEditDescription(e.target.value)} />
                    <label style={{display:'flex', alignItems:'center', gap:'8px', color:'#9aa0b5', cursor:'pointer'}}>
                      <input type="checkbox" checked={!editIsPublic} onChange={(e)=>setEditIsPublic(!e.target.checked)} style={{width:'16px', height:'16px'}} />
                      Приватный список
                    </label>
                    <div style={{display:'flex', gap:'8px', flexWrap:'wrap'}}>
                      <button type="button" onClick={()=>saveEdit(lst.id)}>Сохранить</button>
                      <button type="button" onClick={()=>setEditingId(null)} style={{background:'#dfe1e6', color:'#111'}}>Отмена</button>
                      {!protectedTitles.includes(lst.title?.toLowerCase()) && (
                        <button type="button" onClick={()=>handleDelete(lst.id, lst.title)} style={{background:'#ffdddd', color:'#8b0000'}}>Удалить</button>
                      )}
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
};

export default ListsPage;
