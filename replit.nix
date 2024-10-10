{ pkgs }: {
  deps = [
    pkgs.tree
    pkgs.fltk14
    pkgs.glibcLocales
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.gtk3
    pkgs.gobject-introspection
    pkgs.ghostscript
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.cairo
    pkgs.postgresql
    pkgs.python311  # Adicionando Python 3.11 para compatibilidade com as dependências do projeto
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel

    # Dependências de Python usadas no projeto
    pkgs.python311Packages.flask
    pkgs.python311Packages.flask-login
    pkgs.python311Packages.requests
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.plotly
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.pandas
    pkgs.python311Packages.scikit-learn
    pkgs.python311Packages.bcrypt
    pkgs.python311Packages.flask-limiter
  ];

  # Ambiente do Python com o uso do `python3` e `pip` habilitado.
  shellHook = ''
    export PYTHONPATH="${pkgs.python311}/lib/python3.11/site-packages:$PYTHONPATH"
    export PATH=${pkgs.python311}/bin:$PATH
  '';
}

