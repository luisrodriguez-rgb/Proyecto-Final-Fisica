# Prompts para generar imágenes (ChatGPT y Nano Banana)

Imágenes de apoyo para las diapositivas y el documento impreso. Están en inglés porque los generadores responden
mejor así; debajo de cada una va para qué sirve.

## Consejos para que queden bien

- **Formato:** 16:9 para diapositivas y 4:3 o 3:2 para el documento. Agrega al final del prompt
  `Aspect ratio 16:9.` o `Aspect ratio 4:3.`
- **Mismo estilo en todas:** genera primero la imagen 1 y, en las siguientes, adjúntala y pide
  `Match the visual style, lighting and color palette of the attached image.`
- **Nano Banana (Gemini) edita muy bien imágenes que le subas.** Toma una captura de la escena 3D del simulador y
  pídele que la convierta en un render realista (prompt 8). Así la imagen coincide con lo que muestra la app.
- **Sin marcas:** todos los prompts piden `no logos, no brand badges, no text`. Si aparece un logo, pide
  `remove all logos and badges`.
- **Texto:** los generadores suelen escribir mal en español. Pide la imagen sin texto y pon los títulos y etiquetas
  en la diapositiva.
- **Cita la imagen:** la guía pide citar el contenido hecho con IA. Agrega en el pie de figura, por ejemplo,
  "Imagen generada con ChatGPT (OpenAI), 2026" o "con Gemini (Google), 2026".

---

## 1. Portada: entrada del parqueadero de noche

```
Cinematic wide shot of a modern parking-lot entrance at dusk. A small red five-door city hatchback is stopped
on the asphalt just before a red-and-white boom barrier that is lifting. A square inductive loop is cut into the
pavement under the car; the saw-cut lines glow softly orange, and faint blue magnetic field lines rise from the
loop and bend under the car's steel floor. A slim detector cabinet with a small green display stands on a post
beside the barrier. Wet asphalt with subtle reflections, soft rim lighting, shallow depth of field,
photorealistic, clean composition with empty space on the left for a title. No logos, no brand badges, no text,
no people. Aspect ratio 16:9.
```

Para la portada de la presentación y del documento.

## 2. Corte del pavimento con la espira

```
Technical cutaway illustration of asphalt pavement, cut open to show a narrow saw-cut slot about 6 mm wide and
5 cm deep. At the bottom of the slot lie three turns of insulated copper wire; black sealant fills the slot
above them. A twisted-pair lead-in cable runs from the loop to a small pull box at the curb. Above the
pavement, the flat steel underbody of a small car hovers at 15 cm. Clean isometric view, studio lighting, light
gray background, precise engineering style like a premium product explainer, subtle color: asphalt dark gray,
copper orange, steel blue-gray. No text, no labels, no logos. Aspect ratio 4:3.
```

Para explicar en el documento cómo está instalada la espira. Va bien junto a la figura de Anatomy.

## 3. Campo magnético y corrientes de Foucault

```
Scientific visualization of a square wire loop embedded in pavement, viewed from a low angle. Glowing cyan
magnetic field lines loop up out of the pavement through the center of the coil and curve back down outside it.
Directly above, the steel floor panel of a car flattens the field lines so they run parallel to its underside,
and concentric orange rings of eddy currents glow on the bottom of the steel panel. Dark background, high
contrast, elegant and minimal, like a physics textbook illustration rendered in 3D. No text, no logos.
Aspect ratio 16:9.
```

Para la diapositiva de la física: Faraday, corrientes de Foucault y ley de Lenz.

## 4. Comparación de los dos carros

```
Side-by-side studio comparison of two small five-door city hatchbacks in profile on a light gray floor, both
facing right. Left car: red, slightly lower ride height. Right car: blue, slightly taller ride height. Under each
car, a thin horizontal measuring line highlights the gap between the floor and the car's underbody, emphasizing
that the right car sits higher. Neutral soft studio lighting, minimal, clean, photorealistic. No logos, no brand
badges, no text. Aspect ratio 16:9.
```

Para la diapositiva "Spark (15 cm) frente a Kwid (18 cm)". Las medidas se escriben luego en la diapositiva.

## 5. Sensor inductivo industrial abierto (segundo escenario)

```
Exploded-view product render of a cylindrical industrial inductive proximity sensor (M30 threaded metal
housing). The parts float apart along one axis: plastic sensing face cap, ferrite cup core, copper wound coil,
small green circuit board with the oscillator, threaded stainless-steel housing with two lock nuts, and the cable
gland with a gray cable. A small steel bolt sits in front of the sensing face. Clean white background, soft
shadows, high detail, technical catalog style. No text, no logos. Aspect ratio 4:3.
```

Para la parte de la línea de autopartes y la identificación de materiales.

## 6. Esquema D.E.P.A. como infografía (solo el fondo)

```
Minimal horizontal infographic background with four large rounded panels connected left to right by thin arrows,
each panel with a simple flat icon: 1) a radar-like detection icon over a car silhouette, 2) wavy lines rising
from a metal plate, 3) a sine wave with a lightning symbol, 4) a boom barrier with an alert light. Flat vector
style, soft blue and gray palette, white background, lots of empty space inside each panel for text to be added
later. No text, no letters, no numbers. Aspect ratio 16:9.
```

Las palabras Detección, Emisiones, Propiedades y Alerta se escriben encima, en la diapositiva.

## 7. Aplicaciones reales (collage)

```
Clean 2x2 photo collage of real-world uses of inductive loop detectors: a traffic light intersection with saw-cut
loops visible in the asphalt, a parking garage entrance with a boom barrier, a highway toll lane, and a factory
conveyor belt with metal parts passing an inductive sensor. Consistent daylight color grading, photorealistic.
No logos, no text, no readable signs. Aspect ratio 16:9.
```

Para la diapositiva de contexto de aplicación (insumos).

## 8. Edición: de la escena del simulador a un render realista (Nano Banana)

Sube una captura de la pestaña **Caso: vehículo** con la cámara en "General" y usa:

```
Turn this 3D simulator screenshot into a photorealistic render while keeping exactly the same composition,
camera angle, car position, barrier, detector post and loop location. Replace the flat shapes with realistic
materials: glossy car paint, real tires and rims, textured asphalt with lane paint, a metal boom barrier with
red-and-white stripes. Keep the glowing orange loop in the pavement and the blue magnetic field lines as a subtle
overlay. Remove all on-screen panels, labels and buttons. No logos, no text. Keep the same aspect ratio.
```

Así la imagen de la presentación coincide con lo que se ve en la demo en vivo.
