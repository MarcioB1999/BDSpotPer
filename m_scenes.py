import tkinter as tk
import database as db



class Scene():
    frame : tk.Frame
    
    def __init__(self, **kwargs):
        self.frame = tk.Frame(
            master=kwargs["master"],
            width=640, height=480,

            bg= kwargs.get("bg", "darkblue")
        )
        self._init_elements_()

    def _init_elements_(self): #virtual
        pass
    
    def pack(self):
        self.frame.pack(fill=tk.BOTH)

    def switch_to(self, target, master=None):
        targetscene = target(master=self.frame.master if master is None else master)
        targetscene.pack()
        self.frame.destroy()



class DummyScene(Scene):
    btn_ok : tk.Button

    def _init_elements_(self):
        btn_ok = tk.Button(
            master=self.frame,
            text="OK",
            command=self.on_ok_pressed
        )
        btn_ok.pack(fill=tk.BOTH, padx=10, pady=10)

    def on_ok_pressed(self):
        self.switch_to(MenuScene)



class MenuScene(Scene):
    button1 : tk.Button

    def __init__(self, **kwargs):
        super().__init__(height=480, **kwargs)
    
    def _init_elements_(self):
        self.frame.columnconfigure(0, weight=1)
        #self.frame.rowconfigure([0,1], weight=1, minsize=50)
        
        self.button1 = tk.Button(
            master=self.frame,
            text="Nova Playlist",
            command=self.on_playlist_new
        )

        title = tk.Label(master=self.frame,
            text="Playlists", font="Consolas 20"
        )

        self.button1.grid(row=0, column=0, sticky="ew", padx=50, pady=20)
        title.grid(row=1, column=0, sticky="ew", padx=50, pady=20)

        #dummy
        # tk.Button(
        #     master=self.frame,
        #     text="Dummy",
        #     command=self.on_dummy_pressed
        # ).grid(row=3, column=0, sticky="ew", padx=50, pady=20)

        self._init_playlists_()


    def _init_playlists_(self):
        frame_playlists = tk.Frame(master=self.frame,
            bg="lightblue"
        )
        frame_playlists.columnconfigure([0,1], weight=1, minsize=200)
        
        playlists = db.get_all_playlists()
        
        iter = 0
        for pl in playlists:
            print(pl.id)
            
            lbl = tk.Label(master=frame_playlists,
                text=pl.nome
            )
            lbl.grid(row=iter, column=0)
            
            btn = tk.Button(master=frame_playlists,
                text="Visualizar",
                command=(lambda id=pl.id : self.on_playlist_edit(id))
            )
            btn.id=pl.id
            btn.grid(row=iter, column=1)

            iter+=1
        
        frame_playlists.grid(row=2, column=0, sticky="ew", padx=50, pady=20)    
    

    def pack(self):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def on_dummy_pressed(self):
        self.switch_to(DummyScene)

    def on_playlist_new(self):
        self.switch_to(CreatePlaylistScene)

    def on_playlist_edit(self, id):
        next_scene = PlaylistScene(
            master=self.frame.master,
            row=db.get_playlist_by_id(id)
        )
        self.frame.destroy()
        next_scene.pack()


class PlaylistScene(Scene):
    row : db.pyodbc.Row
    id : int
    name : str
    tracklist : tk.Frame

    def __init__(self, **kwargs):
        self.row = kwargs["row"]
        self.id = self.row.id
        self.name = self.row.nome
        super().__init__(height=480, **kwargs)
    
    def _init_elements_(self):
        #buttons header
        miniframe = tk.Frame(master=self.frame, height=100)
        
        btn_delete = tk.Button(master=miniframe,
            text="Apagar", command=self.on_delete
            )
        btn_delete.pack(side=tk.RIGHT, padx=10)
        
        
        btn_return = tk.Button(master=miniframe,
            text="Voltar", command=self.on_return
            )
        btn_return.pack(side=tk.LEFT, padx=10)
        
        miniframe.pack(side=tk.TOP)
        
        
        #title
        title = tk.Label(master=self.frame,
            text=self.name, font="Consolas 20"
        )
        title.pack(side=tk.TOP)

        #add song button
        btn_add = tk.Button(master=self.frame,
            text="Adicionar Música",
            command = self.on_add_track
        )
        btn_add.pack(side=tk.BOTTOM)
        
        
        #track list
        self._init_track_list_()
        

    def _init_track_list_(self):
        #if self.tracklist: self.tracklist.destroy()
        self.tracklist = tk.Frame(master=self.frame, bg="gray", height="200")
        self.tracklist.columnconfigure([0,1], weight=1, minsize=100)


        tracks = db.get_all_tracks_in_playlist(self.id)

        iter = 0
        for track in tracks:
            lbl = tk.Label(master=self.tracklist,
                text=track.descricao
            )
            btn_del = tk.Button(master=self.tracklist,
                text="Remover",
                command=(lambda a1=self.id, a2=track.album, a3=track.numero_faixa : self.on_remove_track(a1,a2,a3))
            )

            
            btn_play = tk.Button(master=self.tracklist,
                text="Tocar",
                command=(lambda a1=self.id, a2=track.album, a3=track.numero_faixa : self.on_play_track(a1,a2,a3))
            )
            

            lbl.grid(row=iter, column=0)
            btn_del.grid(row=iter, column=1)
            btn_play.grid(row=iter,column=2)
            iter+=1
        
        self.tracklist.pack(side=tk.BOTTOM)
        
    
    def pack(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
    

    def refresh_tracklist(self):
        self.tracklist.destroy()
        self._init_track_list_()
        
        
    def on_play_track(self, playlist_id, row_album, row_num):
        db.play_track_on_playlist(playlist_id, row_album, row_num)


    def on_remove_track(self, playlist_id, row_album, row_num):
        db.remove_track_from_playlist(playlist_id, row_album, row_num)
        self.refresh_tracklist()
    
    def on_add_track(self):
        next_scene = AddToPlaylistAlbumScene(
            master=self.frame.master,
            playlist_row=self.row
        )
        self.frame.destroy()
        next_scene.pack()

    def on_return(self):
        self.switch_to(MenuScene)
    
    def on_delete(self):
        db.delete_playlist(self.id)
        self.switch_to(MenuScene)


class AddToPlaylistAlbumScene(Scene):
    playlist_row : db.pyodbc.Row
    playlist_id : int
    playlist_name : str

    def __init__(self, **kwargs):
        self.playlist_row = kwargs["playlist_row"]
        self.playlist_id = self.playlist_row.id
        self.playlist_name = self.playlist_row.nome
        super().__init__(height=480, **kwargs)
    
    def _init_elements_(self):
        #header
        miniframe = tk.Frame(master=self.frame, bg="darkblue") 
        btn_return = tk.Button(master=miniframe,
            text="Voltar", command=self.on_return
        )
        btn_return.pack(side=tk.TOP,padx=10, pady=2)
        lbl_name = tk.Label(master=miniframe,
            text=f"Adicionar a {self.playlist_name}"
        )
        lbl_name.pack(side=tk.TOP,padx=10, pady=2)
        miniframe.pack(side=tk.TOP)

        #lista de albums
        albumframe = tk.Frame(master=self.frame,
            bg="lightblue"
        )
        albumframe.columnconfigure(0, weight=1, minsize=200)
        albums = db.get_all_albums()
        iter = 0
        for album in albums:
            btn = tk.Button(master=albumframe,
                text=album.descrição,
                command=(lambda al=album.id : self.on_select_album(al))
            )
            btn.grid(row=iter, pady=10)
            iter += 1

        albumframe.pack(side=tk.TOP)
    
    def pack(self):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def on_return(self):
        next_scene = PlaylistScene(
            master=self.frame.master,
            row=self.playlist_row
        )
        self.frame.destroy()
        next_scene.pack()

    def on_select_album(self, album_id):
        #print(f"Album selecionado: {album_id}")
        next_scene = AddToPlaylistTrackScene(
            master=self.frame.master,
            playlist_row=self.playlist_row,
            album_row=db.get_album_from_id(album_id)
        )
        self.frame.destroy()
        next_scene.pack()
    

class AddToPlaylistTrackScene(Scene):
    playlist_row : db.pyodbc.Row
    playlist_id : int
    playlist_name : str

    album_row: db.pyodbc.Row
    album_id: int
    album_name: str

    def __init__(self, **kwargs):
        self.playlist_row = kwargs["playlist_row"]
        self.playlist_id = self.playlist_row.id
        self.playlist_name = self.playlist_row.nome
        self.album_row = kwargs["album_row"]
        self.album_id = self.album_row.id
        self.album_name = self.album_row.descrição
        super().__init__(height=480, **kwargs)
    
    def _init_elements_(self):
        #header
        miniframe = tk.Frame(master=self.frame, bg="darkblue") 
        btn_return = tk.Button(master=miniframe,
            text="Voltar", command=self.on_return
        )
        btn_return.pack(side=tk.TOP,padx=10, pady=2)
        lbl_title = tk.Label(master=miniframe,
            text=f"Adicionar a {self.playlist_name}",
        )
        lbl_title.pack(side=tk.TOP,padx=10, pady=2)
        lbl_title = tk.Label(master=miniframe,
            text=self.album_name,
            font="Consolas 20"
        )
        lbl_title.pack(side=tk.TOP,padx=10, pady=8)
        miniframe.pack(side=tk.TOP)

        self._init_tracklist_()

    def _init_tracklist_(self):
        #lista de faixas
        trackframe = tk.Frame(master=self.frame,
            bg="lightblue"
        )
        trackframe.columnconfigure(0, weight=1, minsize=200)
        tracks = db.get_all_tracks_in_album(self.album_id)
        iter = 0
        for track in tracks:
            btn = tk.Button(master=trackframe,
                text=track.descricao,
                command=(lambda n=track.numero_faixa : self.on_select_track(n))
            )
            btn.grid(row=iter, pady=10)
            iter += 1

        trackframe.pack(side=tk.TOP)
    
    def pack(self):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def on_return(self):
        next_scene = AddToPlaylistAlbumScene(
            master=self.frame.master,
            playlist_row=self.playlist_row,
        )
        self.frame.destroy()
        next_scene.pack()

    def on_select_track(self, track_num):
        db.insert_track_into_playlist(self.playlist_id, self.album_id, track_num)
        #return to playlist scene
        next_scene = PlaylistScene(
            master=self.frame.master,
            row=self.playlist_row
        )
        self.frame.destroy()
        next_scene.pack()
    

class CreatePlaylistScene(Scene):
    entry : tk.Entry
    lbl_error : tk.Label

    def _init_elements_(self):
        #header
        miniframe = tk.Frame(master=self.frame, bg="darkblue") 
        btn_return = tk.Button(master=miniframe,
            text="Voltar", command=self.on_return
        )
        btn_return.pack(side=tk.TOP,padx=10, pady=2)
        lbl_name = tk.Label(master=miniframe,
            text=f"Criar Nova Playlist"
        )
        lbl_name.pack(side=tk.TOP,padx=10, pady=2)
        miniframe.pack(side=tk.TOP)

        self.entry = tk.Entry(master=self.frame,
            width=50
        )
        self.entry.pack(side=tk.TOP)

        self.lbl_error = tk.Label(master=self.frame,
            text="", bg="darkblue", fg="red", width=60, height=2
        )
        self.lbl_error.pack(side=tk.TOP)
    
        btn_create = tk.Button(master=self.frame,
            text="Criar", command=self.on_confirm
        )
        btn_create.pack(side=tk.TOP)



    def on_confirm(self):
        name = self.entry.get()
        #restricoes
        if len(name) > 50:
            self.lbl_error.config(text="Nome deve ser menor que 50 caracteres.")
            self.entry.delete(0, tk.END)
            return
        if len(name) <= 0:
            self.lbl_error.config(text="Nome não pode ser vazio.")
            return
        #rodar
        db.create_playlist(name)
        
        self.switch_to(MenuScene)
    
    def on_return(self):
        self.switch_to(MenuScene)
        
        

