function initializeBubbles(canvasElement, bubbleData,odooContext) {
    var canvas = document.getElementById('renderCanvas');
    var engine = new BABYLON.Engine(canvasElement, true);
    var advancedTexture;
    var bubbleNames = [];
    var currentLevelData = bubbleData; // Memorizza i dati del livello corrente
    var parentLevels = []; // Stack per memorizzare i livelli genitore
    var bubbleParent = [];
    var bubbleHighlight = [];
    var highlightActive = false;
    var hl;
    var createScene = function () {
        var scene = new BABYLON.Scene(engine);
        scene.clearColor = new BABYLON.Color4(1, 0.85, 0.90 ,1);
        hl = new BABYLON.HighlightLayer("hl1", scene);
        var camera = new BABYLON.UniversalCamera("TouchCamera", new BABYLON.Vector3(0, 1, -5), scene);
        camera.setTarget(BABYLON.Vector3.Zero());
        camera.attachControl(canvas, true);
        camera.angularSensibilityX = 1000; // Valore più alto per ridurre la sensibilità sull'asse X
        camera.angularSensibilityY = 1000; // Valore più alto per ridurre la sensibilità sull'asse Y
        camera.speed = 1;
        // Keyframes per l'animazione
        startAnimation();
        var light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(1, 1, 0), scene);
        function startAnimation() {
            var animation = new BABYLON.Animation("cameraAnimation", "position.z", 30, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);

            var keys = []; 
            keys.push({ frame: 0, value: -7 }); // Posizione iniziale della telecamera
            keys.push({ frame: 100, value: -9}); // Telecamera si allontana
            animation.setKeys(keys);

            // Applicazione dell'animazione alla telecamera
            camera.animations.push(animation);

            // Avvia l'animazione
            scene.beginAnimation(camera, 0, 100, false);
        }
        // Funzione per creare il testo sotto la bolla
        function createBubbleText(name, position, visible, image=false) {
            var textureSize = 2048; // Dimensione della texture
            var dynamicTexture = new BABYLON.DynamicTexture("DynamicTexture", textureSize, scene, true);
            dynamicTexture.hasAlpha = true;
            
            var textSize = "bold 200px Arial"; // Dimensione del testo
            var lineHeight = 200; // Altezza della linea
            var words = name.split(" "); // Split the text into words
            var y = 200; // Posizione Y iniziale per il testo
            var imageWidth = 800; // Larghezza dell'immagine
            var imageHeight = 800; // Altezza dell'immagine
            var textX = 200 + imageWidth; // X position for text, after the image
        
            // Disegnare l'immagine dal codice Base64, se fornita
            if (image) {
                var imageSrc = "data:image/png;base64," + image;
                var img = new Image();
                img.onload = function() {
                    // Disegnare l'immagine sulla texture
                    dynamicTexture.getContext().drawImage(this, 0, 0, imageWidth, imageHeight);
                    dynamicTexture.update();
                    
                    // Disegnare il testo dopo che l'immagine è stata caricata
                    var yText = 200; // Y position for text
                    words.forEach(function(word) {
                        dynamicTexture.drawText(word, textX, yText, textSize, "black", "transparent", true);
                        yText += lineHeight; // Spostare giù per la prossima linea
                    });
                };
                img.src = imageSrc;
            } else {
                // Se non c'è immagine, disegna solo il testo
                words.forEach(function(word) {
                    dynamicTexture.drawText(word, 200, y, textSize, "black", "transparent", true);
                    y += lineHeight; // Spostare giù per la prossima linea
                });
            }
        
            var planeSize = 2; // Dimensione del piano
            var plane = BABYLON.Mesh.CreatePlane("TextPlane", planeSize, scene);
            plane.position = new BABYLON.Vector3(position.x, position.y - 2.5, position.z);
            plane.material = new BABYLON.StandardMaterial("TextPlaneMaterial", scene);
            plane.material.diffuseTexture = dynamicTexture;
            plane.material.specularColor = new BABYLON.Color3(0, 0, 0);
            plane.material.emissiveColor = new BABYLON.Color3(1, 1, 1);
            plane.material.backFaceCulling = false;
            
            if (!visible) {
                plane.visibility = 0;
            }
        
        }
        function activateHighlightButton() {
            var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
            
            var container = new BABYLON.GUI.StackPanel();
            container.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
            advancedTexture.addControl(container);
            var button1 = BABYLON.GUI.Button.CreateSimpleButton("but", "My Bubbles");
            button1.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
            button1.width ="128px";
            button1.height = "30px";
            button1.fontSize = 10;
            button1.color = "white";
            button1.background = "grey";
            button1.onPointerClickObservable.add(function(){
                if (highlightActive) {
                    highlightActive = false;
                    bubbleHighlight.forEach(function (bubble, index) {
                        hl.removeMesh(bubble);
                    });
                }
                else {
                    highlightActive = true;
                    bubbleHighlight.forEach(function (bubble, index) {
                        hl.addMesh(bubble, BABYLON.Color3.White());
                    });
                }
            });
            container.addControl(button1);
        }

        function createFirstText(name, image = false,link=false,description=false,id=false) {
            
            var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
            
            var container = new BABYLON.GUI.StackPanel();
            container.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
            advancedTexture.addControl(container);
            var button1 = BABYLON.GUI.Button.CreateSimpleButton("but", name);
            button1.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
            button1.width ="128px";
            button1.height = "30px";
            button1.fontSize = 10;
            button1.color = "white";
            button1.background = "grey";
            button1.onPointerClickObservable.add(function(){
                if (parentBubble.length>0) {
                    clearScene(advancedTexture); 
                }
                if (parentLevels.length > 0) {
                    currentLevelData = parentLevels.pop(); // Torna al livello genitore
                    parentBubble = bubbleParent.pop();
                    if (parentBubble) {
                        advancedTexture = createFirstText(parentBubble.name,parentBubble.image,parentBubble.link,parentBubble.description,parentBubble.id);
                    }
                    showBubbles(currentLevelData);
                    startAnimation();
                }
            });
            container.addControl(button1);
            if (image) {
                var base64ImageString = "data:image/png;base64," + image;
                var imageControl = new BABYLON.GUI.Image("image", base64ImageString);
                imageControl.width = "128px";
                imageControl.height = "128px";
                imageControl.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
                container.addControl(imageControl);
            }
            /*if (description) {
                var textBlock = new BABYLON.GUI.TextBlock();
                textBlock.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
                textBlock.text = description;
                textBlock.color = "black";
                textBlock.textWrapping = true; 
                textBlock.fontSize = 10;
                textBlock.width ="128px";
                textBlock.height ="128px";
                container.addControl(textBlock);
            }*/
            if (link) {
                var button2 = BABYLON.GUI.Button.CreateSimpleButton("but", "Open");
                button2.width = "128px";
                button2.fontSize = 10;
                button2.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
                button2.height ="30px";
                button2.color = "white";
                button2.background = "grey";
                button2.onPointerClickObservable.add(function() {
                    odooContext.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'bubble', // Replace with your model
                        res_id: id, // ID of the record to open
                        views: [[false, 'form']],
                        target: 'new'
                    });
                });
                container.addControl(button2);
            }     
            return advancedTexture;
        }
        // Funzione per creare una bolla
        function createBubble(name, position, size, content,color,alpha=0, image=false,highlight=false) {
            bubbleNames.push(name);
            var bubble = BABYLON.MeshBuilder.CreateSphere(name, {diameter: size}, scene);
            bubble.position = position;
            bubble.material = new BABYLON.StandardMaterial(name + "Material", scene);
            bubble.material.diffuseColor = new BABYLON.Color3.FromHexString(color);
            if (alpha == 0) {
                bubble.material.alpha = 0.6; // Rendere la bolla trasparente
            }
            if (highlight ) {
                bubbleHighlight.push(bubble);
            }
            // Calcolare la posizione delle bolle contenute
            var innerBubbleSize = size / 3; // Ridurre la dimensione delle bolle interne
            content.forEach(function (innerBubble, index) {
                if (index<=4) {
                    var angle = Math.PI * 2 * index / (content.length < 5 ? content.length : 5); // Angolo per distribuire le bolle internamente
                    var innerPosition = position.add(new BABYLON.Vector3(Math.cos(angle) * size / 4, Math.sin(angle) * size / 4, 0));
                    var image = innerBubble.image ? innerBubble.image : false;
                    createBubble(innerBubble.name, innerPosition, innerBubbleSize, innerBubble.content,innerBubble.color,0.8,image,innerBubble.highlight);
                }
            });
        }
        function clearScene(advancedTexture) {
            while (scene.meshes.length > 0) {
                scene.meshes[0].dispose();
            }
            if (advancedTexture) {
                advancedTexture.dispose();
            }
        }
        function showBubbles(bubblesData, parentPosition) {
            var startPosition = new BABYLON.Vector3(-2, 0, 0);
            bubblesData.forEach(function (bubbleData, index) {
                var image = bubbleData.image ? bubbleData.image : false;
                createBubble(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 3, 0, 0)), bubbleData.size, bubbleData.content,bubbleData.color,0,image,bubbleData.highlight);
                createBubbleText(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 3, 0, 0)), true,image);

            });
            
        }
        // Gestione clic su una bolla
        scene.onPointerDown = function (evt, pickResult) {
            if (pickResult.hit && bubbleNames.includes(pickResult.pickedMesh.name)) {
                var selectedBubbleData = currentLevelData.find(b => b.name === pickResult.pickedMesh.name);
                if (selectedBubbleData && selectedBubbleData.content.length > 0) {
                    // Memorizza il livello genitore
                    bubbleParent.push(selectedBubbleData);
                    parentLevels.push(currentLevelData);
                    currentLevelData = selectedBubbleData.content;
                    clearScene(advancedTexture);
                    showBubbles(currentLevelData);
                    advancedTexture = createFirstText(selectedBubbleData.name,selectedBubbleData.image,selectedBubbleData.link,selectedBubbleData.description,selectedBubbleData.id);
                    startAnimation();
                }
                if (selectedBubbleData && selectedBubbleData.content.length == 0) {
                    odooContext.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'bubble', // Replace with your model
                        res_id: selectedBubbleData.id, // ID of the record to open
                        views: [[false, 'form']],
                        target: 'new'
                    });
                }
            }
        };
        if (Array.isArray(currentLevelData) && currentLevelData.length > 0) {
            showBubbles(currentLevelData);
            if (currentLevelData.length == 1) {
                advancedTexture = createFirstText(currentLevelData[0].name,currentLevelData[0].image,currentLevelData[0].link,currentLevelData[0].description,currentLevelData[0].id);
            }
            activateHighlightButton();
        }
        return scene;
    };

    var scene = createScene();

    engine.runRenderLoop(function () {
        scene.render();
    });

    window.addEventListener('resize', function () {
        engine.resize();
    });
}
window.initializeBubbles = initializeBubbles;