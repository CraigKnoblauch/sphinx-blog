import { useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { RocketLaunch } from 'src/components/RocketLaunch.jsx'
import { ExhaustParticle } from 'src/components/ExhaustParticle.jsx'
import { FlamesDemonstration } from 'src/components/FlamesDemonstration.jsx'

In November 2019, the NG-12 ISS resupply launch carried my team's satellite to space! It was a transformative experience. Press the big red button on the window below!

<div className="h-150">
<Canvas>
    <ambientLight />
    <perspectiveCamera position={[-0.2, 3.6, 6.5]} />
    <RocketLaunch />
</Canvas>
</div>

The entire scene is made possible with ThreeJS. The models, animations, and most of the materials were created in Blender. 

# Animations
Animations in ThreeJS are straightforward. The render loop is accessible with the useFrame hook. As long as you associate a ref with the entities in the 3JS scene you want to animate, all you have to do is update the desired property during the render loop. The code below shows you how to use this method to rotate a cube.

```js
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export default function RotatingCube() {
    const ref = useRef();
    useFrame(() => {
        if (ref.current) {
            ref.current.rotation.y += 0.01;
            ref.current.rotation.x += 0.01;
        }
    })

    return (
        <>
            <ambientLight />
            <perspectiveCamera position={[0, 0, 5]} />
            <mesh ref={ref} rotation={[0, 0, 0]}>
                <boxGeometry args={[1, 1, 1]} />
                <meshNormalMaterial/>
            </mesh>
        </>
    );
}
```

This is the most common approach. But what if you have a bunch of things you want to animate? What if you want to have some mildly complex behaviors like a rocket that accelerates upward? That's gonna require a lot of code. If you're building test cases, that's going to require a bunch of tests. Yes maybe you can tuck it away in isolated components, but what if you want to change it in the future? What if you want to add a slight spin to the rocket or add an entirely new animation? The code balloons, and it becomes harder and harder to change, understand, and maintain. 

## Blender defined animations
While I was working on a different project, I realized that I could probably define my animations in Blender, export them with the rocket launch gltf file, and play them in the scene. That's exactly what I've done here. I keyframed the positions of the rocket, cradle, and launch button for the beginning and the end of the animation. Blender provides a curve editor, which allows you to play with the animation transitions in a much more intuitive way compared to changing values in code. 

![](/pics/blender-rocket-animation-editor.png)

Once the animation is exported from Blender, I can use the [built-in animation system ThreeJS provides](https://threejs.org/docs/#manual/en/introduction/Animation-system). Now, playing the animation is as simple as `action.play()`. Resetting the animation is as simple as `action.reset()`. No more complex state tracking. And the management of the animation is passed off to the ThreeJS library, which means much less for me to test. 

```jsx
const { nodes, animations } = useGLTF('/models/rocket-launch.glb')

const rocketRef = useRef(new THREE.Object3D())

function startLaunch() {
    const rocketMixer = new THREE.AnimationMixer(rocketRef.current)

    const rocketAction = rocketMixer.clipAction(animations.find(animation => animation.name === 'rocketAction'))
                                    .setLoop(THREE.LoopOnce, 0)
    rocketAction.clampWhenFinished = true 
    
    rocketAction.play()
}

useFrame((state, delta) => {
    rocketMixer?.update(delta)
})
```

## Procedural exhaust
The exhaust was interesting to implement. Originally, I was thinking of implementing something close to this

![](/pics/antares-exhaust-ref.png)

The problem? Exhaust smoke of that kind would most likely have to be implemneted as a GLSL shader. Shaders are fun for sure, but one of that complexity is a bit too much for me at the moment. I also couldn't find a method to transpile a blender shader into a GLSL shader compatible with WebGL. This doesn't mean that a method doesn't exist, but I couldn't find one at the time.

I decided to play around with a collection of meshes to create a cartoon smoke effect.

I decided to use dodecahedrons for the base smoke particle. This is a standard mesh type in ThreeJS, which makes it very easy to instantiate them in my scene. I took three of the gray matcaps I have from the rest of my [portfolio project](lessons-from-a-3d-portfolio.mdx) and applied them to the dodecahedrons. 

{/* Dodecehedron examples*/}
{/* Formatting not quite working TODO
<div class="flex flex-row justify-between h-100 gap-4 items-center">
    <div class="flex flex-col items-center">
        <img src="/matcaps/rock-gray.png" width={100} height={100}/>
        <Canvas>
            <ambientLight />
            <perspectiveCamera position={[0, 0, 1]} />
            <ExhaustParticle color={"rock-gray"} />
        </Canvas>
    </div>
    <div class="flex flex-col items-center">
        <img src="/matcaps/phx-gray.png" width={100} height={100}/>
        <Canvas>
            <ambientLight />
            <perspectiveCamera position={[0, 0, 1]} />
            <ExhaustParticle color={"phx-gray"} />
        </Canvas>
    </div>
    <div class="flex flex-col items-center">
        <img src="/matcaps/dish-support.png" width={100} height={100}/>
        <Canvas>
            <ambientLight />
            <perspectiveCamera position={[0, 0, 1]} />
            <ExhaustParticle color={"dish-support"} />
        </Canvas>
    </div>
</div>
*/}

To make this collection appear as exhaust, each particle would have to follow a path similar to:

1. Hive a high velocity away from the launch platform.
2. Have a small size when first originating from the launch platform.
3. Have a slight deviation to the right or left.
4. Lose the horizantal velocity away from the platform and float up.
5. Grow in size through their lifetime.

Each particle would have to take a slightly different path, but stay within some set bounds.

I generated one particle per frame. That quickly becomes a lot of mesh objects. Two many, and we're going to start bogging down the client's browser. I capped the number of exhaust particles shown at any one time to 100, and implemented a FIFO queue to mange that. When a smoke particle was popped out of the queue, it was removed from the scene and deleted. Also, for each mesh, it received one of three matcap objects. This means for this entire animation, there's only 100 Mesh objects and 3 material objects in memory.

Tucked away in the back of the model is a single plane mesh. When the scene is active, this plane isn't visible. It's purpose is to give us a normal vector to use for a particle's initial velocity vector. With this method, I can create the exhaust animation independent from its implementation in the world. That gives me a lot of flexibility when I'm modifying the rocket launch scene in Blender.  


## Flames shader
The flames are a GLSL shader. Shaders are freaking wild! They give you ultimate flexibility over exactly where verticles are drawn, and how the triangles drawn between vertices are colored. The flames shader I created combine a few techniques together.

First, the base mesh was specifically designed in blender to be deformable along the vertical axis. The positions of bottom vertices are driven with perlin noise. At each timestep, a pixel value is extracted from the noise texture, and drives the displacement of the verticles at the bottom of the base mesh. The two flame columns use the same perlin texture, but their pixel columns are different. This is what yields the difference in displacement between the two columns of flame. The base mesh was also unwrapped such that the seam of the UV map does not face the viewer.

{/* base mesh image that shows loop cuts */}
![](/pics/flames-base-mesh.png)

Second, the texture of the flame columns is another noise texture that has been stretched and repeats infinitely across the surface of the mesh. A color gradient is applied so that the top vertices are yellow, and the color shifts to blue at the bottom. The final material carries a transparent property. That gives a translucent effect to the flames. 

{/* Perlin noise textures side by side*/}
<div class="flex flex-row justify-between h-100 w-full gap-4">
    <div class="flex flex-col">
        <img src="/textures/jumpy-perlin.png" width={300} height={300}/>
        <div>Perlin noise used for flame jumpiness</div>
    </div>
    <div class="flex flex-col">
        <img src="/textures/perlin.png" width={300} height={300}/>
        <div>Perlin noise used for visible texture</div>
    </div>
</div>

Combine those features together, and you get rocket flames!

{/* update */}
