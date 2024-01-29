function initializeBubbles(canvasElement, bubbleData) {
    var canvas = document.getElementById('renderCanvas');
    var engine = new BABYLON.Engine(canvasElement, true);


    var currentLevelData = bubbleData; // Memorizza i dati del livello corrente
    var parentLevels = []; // Stack per memorizzare i livelli genitore

    var createScene = function () {
        var scene = new BABYLON.Scene(engine);
        scene.clearColor = new BABYLON.Color4(1, 0.85, 0.90 ,1);
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
        function createBubbleText(name, position, visible, image = false) {
            var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
        
            // Crea un blocco di testo per il nome
            var textBlock = new BABYLON.GUI.TextBlock();
            textBlock.text = name;
            textBlock.color = "black";
            textBlock.fontSize = 24;
            textBlock.top = position.y - 100; // Aggiusta la posizione
            textBlock.left = position.x;
            advancedTexture.addControl(textBlock);
        
            // Crea un pulsante o un blocco di testo per il link cliccabile
            var linkBlock = new BABYLON.GUI.TextBlock();
            linkBlock.text = "Clicca qui per maggiori informazioni";
            linkBlock.color = "blue";
            linkBlock.fontSize = 18;
            linkBlock.top = position.y - 130; // Aggiusta la posizione
            linkBlock.left = position.x;
            linkBlock.onPointerDownObservable.add(function() {
                window.open("https://www.example.com", "_blank");
            });
            advancedTexture.addControl(linkBlock);
        
            // Crea un'immagine se fornita
            if (image) {
                var base64ImageString = "data:image/png;base64," + image;
                var imageControl = new BABYLON.GUI.Image("image", base64ImageString);
                imageControl.width = "100px";
                imageControl.height = "100px";
                imageControl.top = position.y - 170; // Aggiusta la posizione
                imageControl.left = position.x;
                advancedTexture.addControl(imageControl);
            }
        
            // Imposta la visibilità
            textBlock.isVisible = visible;
            linkBlock.isVisible = visible;
            if (image) {
                imageControl.isVisible = visible;
            }
        }

        // Funzione per creare una bolla
        function createBubble(name, position, size, content,color,alpha=0, image=false) {
            var bubble = BABYLON.MeshBuilder.CreateSphere(name, {diameter: size}, scene);
            bubble.position = position;
            bubble.material = new BABYLON.StandardMaterial(name + "Material", scene);
            bubble.material.diffuseColor = new BABYLON.Color3.FromHexString(color);
            if (alpha == 0) {
                bubble.material.alpha = 0.6; // Rendere la bolla trasparente
            }
            


            // Calcolare la posizione delle bolle contenute
            var innerBubbleSize = size / 3; // Ridurre la dimensione delle bolle interne
            content.forEach(function (innerBubble, index) {
                if (index<=4) {
                    var angle = Math.PI * 2 * index / content.length; // Angolo per distribuire le bolle internamente
                    var innerPosition = position.add(new BABYLON.Vector3(Math.cos(angle) * size / 4, Math.sin(angle) * size / 4, 0));
                    var image = innerBubble.image ? innerBubble.image : false;
                    createBubble(innerBubble.name, innerPosition, innerBubbleSize, innerBubble.content,innerBubble.color,0.8,image);
                }
            });
        }
        function clearScene() {
            while (scene.meshes.length > 0) {
                scene.meshes[0].dispose();
            }
        }
        function showBubbles(bubblesData, parentPosition) {
            clearScene(); 

            var startPosition = new BABYLON.Vector3(-2, 0, 0);
            bubblesData.forEach(function (bubbleData, index) {
                var image = bubbleData.image ? bubbleData.image : false;
                createBubble(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 3, 0, 0)), bubbleData.size, bubbleData.content,bubbleData.color,0,image);
                createBubbleText(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 3, 0, 0)), true,image);

            });
        }

        

        // Gestione clic su una bolla
        scene.onPointerDown = function (evt, pickResult) {
            if (pickResult.hit && pickResult.pickedMesh.name.startsWith("Bolla")) {
                var selectedBubbleData = currentLevelData.find(b => b.name === pickResult.pickedMesh.name);
                if (selectedBubbleData && selectedBubbleData.content.length > 0) {
                     // Memorizza il livello genitore
                    parentLevels.push(currentLevelData);
                    currentLevelData = selectedBubbleData.content;
                    clearScene(); 
                    showBubbles(currentLevelData);
                    document.getElementById("backButton").style.display = 'block';
                    startAnimation();
                }
            }
        };

        
        document.getElementById("backButton").addEventListener("click", function() {
            if (parentLevels.length > 0) {
                currentLevelData = parentLevels.pop(); // Torna al livello genitore
                showBubbles(currentLevelData);
                startAnimation();
            }
            this.style.display = parentLevels.length > 0 ? 'block' : 'none';
        });

        if (Array.isArray(currentLevelData) && currentLevelData.length > 0) {
            showBubbles(currentLevelData);
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