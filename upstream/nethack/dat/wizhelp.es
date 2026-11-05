Referencia Rápida del Modo Debug:

^E  ==  detectar puertas secretas y trampas cercanas
^F  ==  mapear el nivel; revela trampas y pasillos secretos, pero no puertas secretas
^G  ==  crear monstruo por nombre o clase
^I  ==  identificar objetos en la mochila
^T  ==  teletransporte dentro del nivel
^V  ==  teletransporte entre niveles; '?' muestra menú de destinos especiales
^W  ==  pedir un deseo: objeto, trampa o un conjunto limitado de terreno
^X  ==  mostrar estado, atributos y características (iluminación extendida)

#debugfuzzer    == set game to run on autopilot; keeps going until failure;
                   eleva los avisos imposibles a pánico
#levelchange    == set hero's experience level
#lightsources   == show mobile light sources
#migratemons    == show migrating monsters; [Opt] potentially create some
#panic          == panic test (warning: current game will be terminated)
#polyself       == polymorph self
#stats          == show memory statistics
#terrain        == show current level (more options than in normal play)
#timeout        == look at timeout queue and hero's timed intrinsics
#vision         == show vision array
#wizborn        == show monster birth/death/geno/extinct stats
#wizcast        == cast any spell
#wizdispmacros  == [Opt] check internal display classifications
#wizfliplevel   == transpose the current dungeon level
#wizintrinsic   == set selected intrinsic timeouts
#wizkill        == remove monster(s) from play
#wizloaddes     == load and execute a special level description lua script
#wizloadlua     == load and execute a lua script
#wizmakemap     == recreate the current dungeon level
#wizmondiff     == [Opt] check for discrepancies in monster difficulty ratings
#wizobjprobs    == [Opt] list actual probabilities of item generation
#wizrumorcheck  == validate rumor indexing; also show first, second, and last
                   grabados, epitafios y monstruos alucinatorios aleatorios
#wizseenv       == show map locations' seen vectors
#wizsmell       == smell a monster
#wiztelekinesis == magically shove a monster
#wizwhere       == show dungeon placement of all special levels
#wmode          == show wall modes

Opciones:
debug_hunger    == desactiva el hambre del héroe
debug_mongen    == desactiva la generación aleatoria de monstruos
debug_overwrite_stairs
                == permite reemplazar escaleras por otro terreno
monpolycontrol  == pide nueva forma cada vez que un monstruo cambia de forma
sanity_check    == evalúa monstruos, objetos y mapa antes de cada turno
wizweight       == aumenta las descripciones de objeto con el peso del objeto

[Opt] = disponible condicionalmente según opciones de compilación
