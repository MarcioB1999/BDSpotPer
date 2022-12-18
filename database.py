import pyodbc# as dbc

opt = {
    'server_name': "DESKTOP-AARE28R\SQLEXPRESS",
    'db_name': "BDSpotPer",
    'trusted': 'yes'
}

conn = pyodbc.connect('Driver={SQL Server};'+
    f'Server={opt["server_name"]};'+
    f'Database={opt["db_name"]};'+
    'Trusted_Connection=yes;' 
)

cursor = conn.cursor()

def get_all_playlists():
    result = cursor.execute('select * from playlist')
    rows = result.fetchall()
    return rows

def get_playlist_by_id(id):
    result = cursor.execute('select * from playlist where playlist.id=(?)', id)
    row = result.fetchone()
    if row: return row

def get_all_tracks_in_playlist(id):
    result = cursor.execute(
    """SELECT faixa.*\n
        FROM playlist\n
        INNER JOIN pertence_playlist pp\n
        ON playlist.id=pp.playlist\n
        INNER JOIN faixa\n
        ON faixa.numero_faixa=pp.numero_faixa\n
        AND faixa.album=pp.album\n
        WHERE playlist.id = ?""", id
    )
    tracks = result.fetchall()
    return tracks

def insert_track_into_playlist(playlist, album, track):
    cursor.execute(
    """IF NOT EXISTS (SELECT * FROM pertence_playlist\n
        WHERE playlist=? AND album=? AND numero_faixa=?)\n
        INSERT INTO PERTENCE_PLAYLIST(playlist, album, numero_faixa)\n
        VALUES (?,?,?)""", playlist, album, track, playlist, album, track
    )
    cursor.commit()

def remove_track_from_playlist(playlist, album, track):
    cursor.execute(
        f"DELETE FROM pertence_playlist WHERE playlist=? AND album=? AND numero_faixa=?",
        playlist, album, track 
    )
    cursor.commit()

def get_all_albums():
    result = cursor.execute(
        "SELECT * FROM album"
    )
    rows = result.fetchall()
    return rows

def get_album_from_id(id):
    result = cursor.execute('select * from album where id=(?)', id)
    row = result.fetchone()
    if row: return row

def get_all_tracks_in_album(album_id):
    result = cursor.execute(
        "SELECT * FROM faixa WHERE album=?",album_id
    )
    rows = result.fetchall()
    return rows

def delete_playlist(id):
    cursor.execute(
    """DELETE FROM pertence_playlist WHERE playlist=?;\n
        DELETE FROM playlist WHERE id=?;""", id, id
    )
    cursor.commit()

def create_playlist(name):
    cursor.execute(
    """INSERT INTO playlist (id, nome, data_criacao) VALUES\n
        ((SELECT MAX(id)+1 FROM playlist),?, getdate()); 
    """, name
    )
    cursor.commit()
    
def play_track_on_playlist(playlist, album, track):
    cursor.execute(
        """EXEC qtd_tocada ?, ?, ?""",
        track,album,playlist
    )
    cursor.commit()
    cursor.execute(
        """EXEC ultima_vez_tocada ?, ?, ?""",
        track,album,playlist
    )
    cursor.commit()



#get_all_tracks_in_playlist(id)

#cursor.execute('SELECT * FROM faixa')              
#for i in cursor: print(i) 