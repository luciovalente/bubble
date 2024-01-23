function initializeBubbles(canvasElement, bubbleData) {
    var canvas = document.getElementById('renderCanvas');
    var engine = new BABYLON.Engine(canvasElement, true);


    var currentLevelData = bubbleData; // Memorizza i dati del livello corrente
    var parentLevels = []; // Stack per memorizzare i livelli genitore

    var createScene = function () {
        var scene = new BABYLON.Scene(engine);
        scene.clearColor = new BABYLON.Color4(1, 0.85, 0.90 ,1);
        var camera = new BABYLON.UniversalCamera("UniversalCamera", new BABYLON.Vector3(0, 1, -5), scene);
        camera.setTarget(BABYLON.Vector3.Zero());
        camera.attachControl(canvas, true);
        camera.angularSensibilityX = 1000; // Valore più alto per ridurre la sensibilità sull'asse X
        camera.angularSensibilityY = 1000; // Valore più alto per ridurre la sensibilità sull'asse Y
        camera.speed = 1;
        // Keyframes per l'animazione
        var animation = new BABYLON.Animation("cameraAnimation", "position.z", 30, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_CONSTANT);

        var keys = []; 
        keys.push({ frame: 0, value: -5 }); // Posizione iniziale della telecamera
        keys.push({ frame: 100, value: -8 }); // Telecamera si allontana
        animation.setKeys(keys);

        // Applicazione dell'animazione alla telecamera
        camera.animations.push(animation);

        // Avvia l'animazione
        scene.beginAnimation(camera, 0, 100, false);
        var light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(1, 1, 0), scene);

        // Funzione per creare il testo sotto la bolla
        function createBubbleText(name, position, visible) {
            var dynamicTexture = new BABYLON.DynamicTexture("DynamicTexture", 512, scene, true);
            dynamicTexture.hasAlpha = true; // Impostare la trasparenza della texture
            dynamicTexture.drawText(name, null, null, "bold 40px Arial", "black", "transparent", true);

            var plane = BABYLON.Mesh.CreatePlane("TextPlane", 2, scene);
            plane.position = new BABYLON.Vector3(position.x, position.y - 1.5, position.z); // Posizionare il piano del testo sotto la bolla
            plane.material = new BABYLON.StandardMaterial("TextPlaneMaterial", scene);
            plane.material.diffuseTexture = dynamicTexture;
            plane.material.specularColor = new BABYLON.Color3(0, 0, 0);
            plane.material.emissiveColor = new BABYLON.Color3(1, 1, 1);
            plane.material.backFaceCulling = false;
            if (!visible) {
                plane.visibility = 0; // Rendi il testo invisibile se non è nel livello corrente
            }
        }

        // Funzione per creare una bolla
        function createBubble(name, position, size, content,color,alpha=0) {
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
                    createBubble(innerBubble.name, innerPosition, innerBubbleSize, innerBubble.content,innerBubble.color,0.8);
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

            var startPosition = parentPosition || new BABYLON.Vector3(-2, 0, 0);
            bubblesData.forEach(function (bubbleData, index) {
                createBubble(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 2, 0, 0)), 2, bubbleData.content,bubbleData.color);
                createBubbleText(bubbleData.name, startPosition.add(new BABYLON.Vector3(index * 2, 0, 0)), true);

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
                }
            }
        };

        
        document.getElementById("backButton").addEventListener("click", function() {
            if (parentLevels.length > 0) {
                currentLevelData = parentLevels.pop(); // Torna al livello genitore
                showBubbles(currentLevelData);
            }
            this.style.display = parentLevels.length > 0 ? 'block' : 'none';
        });

        showBubbles(currentLevelData);

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