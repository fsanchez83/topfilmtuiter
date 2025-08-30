import time

t = time.time()
# Script 01
try:
  exec(open("ParticipantesFinalesTFTLB_requests.py").read())
except:
  print("Ha ocurrido un error en ParticipantesFinales")
else:
  print("Ejecución correcta de ParticipantesFinales")

# Script 02
try:
  exec(open("Top_FilmTuiter.py").read())
except:
  print("Ha ocurrido un error en Top_FilmTuiter")
else:
  print("Ejecución correcta de Top_FilmTuiter")

# Script 03
try:
  exec(open("validateFilms.py").read())
except:
  print("Ha ocurrido un error en validateFilms")
else:
  print("Ejecución correcta de validateFilms")

# Script 04
try:
  exec(open("createDatasetTFT.py").read())
except:
  print("Ha ocurrido un error en createDataset")
else:
  print("Ejecución correcta de createDataset")

# Script 05
try:
  exec(open("TopFilmTinderCB_hib.py").read())
except:
  print("Ha ocurrido un error en TopFilmTinder")
else:
  print("Ejecución correcta de TopFilmTinder")

# # Script 06
# try:
#   exec(open("seguidoresLB.py").read())
# except:
#   print("Ha ocurrido un error en seguidoresLB")
# else:
#   print("Ejecución correcta de seguidoresLB")
#
# # Script 07
# try:
#   exec(open("seguidoresLB_filtroTFT.py").read())
# except:
#   print("Ha ocurrido un error en seguidoresLB_filtroTFT")
# else:
#   print("Ejecución correcta de seguidoresLB_filtroTFT")
#
# # Script 08
# try:
#   exec(open("datos_usuario.py").read())
# except:
#   print("Ha ocurrido un error en datos_usuario")
# else:
#   print("Ejecución correcta de datos_usuario")

elapsed = time.time() - t
print(elapsed)
