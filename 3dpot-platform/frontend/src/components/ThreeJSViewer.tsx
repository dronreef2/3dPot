// Three.js 3D Model Viewer Component
import React, { Suspense, useRef, useEffect, useState, useCallback } from 'react';
import { Canvas, useFrame, useLoader, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  Environment, 
  ContactShadows, 
  Text,
  Html,
  PerspectiveCamera,
  Grid,
  Stats,
  useProgress
} from '@react-three/drei';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { Model3D, Geometry, ViewportSettings } from '../types/model3d';
import { motion, AnimatePresence } from 'framer-motion';

// Loading component
const Loader = () => {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex flex-col items-center p-6 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-sm font-medium text-gray-700">Loading 3D Model... {Math.round(progress)}%</p>
      </div>
    </Html>
  );
};

// Individual geometry component
interface GeometryComponentProps {
  geometry: Geometry;
  material: THREE.Material;
}

const GeometryComponent: React.FC<GeometryComponentProps> = ({ geometry, material }) => {
  const meshRef = useRef<THREE.Mesh>(null!);

  const createGeometry = useCallback(() => {
    const params = geometry.parameters;
    let geom: THREE.BufferGeometry;

    switch (geometry.type) {
      case 'box':
        geom = new THREE.BoxGeometry(
          params.width || 1,
          params.height || 1,
          params.depth || 1,
          Math.floor((params.segments || 16) / 4),
          Math.floor((params.segments || 16) / 4),
          Math.floor((params.segments || 16) / 4)
        );
        break;

      case 'sphere':
        geom = new THREE.SphereGeometry(
          params.radius || 0.5,
          params.segments || 32,
          Math.floor((params.segments || 32) / 2)
        );
        break;

      case 'cylinder':
        geom = new THREE.CylinderGeometry(
          params.radiusTop || params.radius || 0.5,
          params.radiusBottom || params.radius || 0.5,
          params.height || 1,
          params.segments || 32
        );
        break;

      case 'cone':
        geom = new THREE.ConeGeometry(
          params.radius || 0.5,
          params.height || 1,
          params.segments || 32
        );
        break;

      case 'torus':
        geom = new THREE.TorusGeometry(
          params.radius || 1,
          params.tube || 0.1,
          params.radialSegments || 16,
          params.tubularSegments || 100
        );
        break;

      default:
        // Custom geometry
        if (geometry.vertices && geometry.faces) {
          geom = new THREE.BufferGeometry();
          const vertices = new Float32Array(geometry.vertices);
          geom.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
          
          if (geometry.faces) {
            const indices = new Uint16Array(geometry.faces);
            geom.setIndex(new THREE.BufferAttribute(indices, 1));
          }
          
          if (geometry.normals) {
            const normals = new Float32Array(geometry.normals);
            geom.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
          }

          geom.computeVertexNormals();
        } else {
          geom = new THREE.BoxGeometry(1, 1, 1);
        }
    }

    return geom;
  }, [geometry]);

  const geometry_3d = createGeometry();

  useFrame(() => {
    if (meshRef.current) {
      // Apply rotation if auto-rotate is enabled
      meshRef.current.rotation.x += 0.01;
    }
  });

  return (
    <mesh
      ref={meshRef}
      geometry={geometry_3d}
      material={material}
      position={[geometry.position.x, geometry.position.y, geometry.position.z]}
      rotation={[geometry.rotation.x, geometry.rotation.y, geometry.rotation.z]}
      scale={[geometry.scale.x, geometry.scale.y, geometry.scale.z]}
      castShadow
      receiveShadow
    />
  );
};

// Model component that renders all geometries
interface Model3DComponentProps {
  model: Model3D;
  wireframe?: boolean;
  showBoundingBox?: boolean;
}

const Model3DComponent: React.FC<Model3DComponentProps> = ({ 
  model, 
  wireframe = false, 
  showBoundingBox = false 
}) => {
  const materialsMap = useRef<Map<string, THREE.Material>>(new Map());

  // Create materials
  useEffect(() => {
    model.materials.forEach(mat => {
      let material: THREE.Material;
      
      const isTransparent = mat.transparent && mat.opacity && mat.opacity < 1;
      const hasTexture = mat.textureUrl || mat.normalMapUrl;

      if (hasTexture) {
        // Texture-based material (simplified)
        material = new THREE.MeshStandardMaterial({
          color: mat.color,
          metalness: mat.metalness || 0,
          roughness: mat.roughness || 1,
          transparent: isTransparent,
          opacity: mat.opacity || 1,
          wireframe
        });
      } else {
        // Standard material
        material = new THREE.MeshStandardMaterial({
          color: mat.color,
          metalness: mat.metalness || 0,
          roughness: mat.roughness || 1,
          transparent: isTransparent,
          opacity: mat.opacity || 1,
          emissive: mat.emissive || '#000000',
          emissiveIntensity: mat.emissiveIntensity || 0,
          wireframe
        });
      }

      materialsMap.current.set(mat.id, material);
    });

    return () => {
      // Cleanup materials
      materialsMap.current.forEach(material => material.dispose());
    };
  }, [model.materials, wireframe]);

  // Calculate bounding box for the entire model
  const boundingBox = React.useMemo(() => {
    const box = new THREE.Box3();
    model.geometries.forEach(geometry => {
      const size = new THREE.Vector3(
        geometry.parameters.width || geometry.parameters.radius || 1,
        geometry.parameters.height || geometry.parameters.radius || 1,
        geometry.parameters.depth || geometry.parameters.radius || 1
      );
      const center = new THREE.Vector3(
        geometry.position.x,
        geometry.position.y,
        geometry.position.z
      );
      
      const geometryBox = new THREE.Box3();
      geometryBox.setFromCenterAndSize(center, size);
      box.union(geometryBox);
    });
    return box;
  }, [model.geometries]);

  return (
    <group>
      {/* Render all geometries */}
      {model.geometries.map((geometry, index) => {
        const material = materialsMap.current.get(geometry.materialId);
        if (!material) return null;

        return (
          <GeometryComponent
            key={`${geometry.id}_${index}`}
            geometry={geometry}
            material={material}
          />
        );
      })}

      {/* Bounding box */}
      {showBoundingBox && (
        <mesh>
          <boxGeometry 
            args={[
              boundingBox.getSize(new THREE.Vector3()).x,
              boundingBox.getSize(new THREE.Vector3()).y,
              boundingBox.getSize(new THREE.Vector3()).z
            ]}
          />
          <meshBasicMaterial 
            color="#00ff00" 
            wireframe 
            transparent 
            opacity={0.5} 
          />
          <primitive 
            object={new THREE.Vector3(
              boundingBox.getCenter(new THREE.Vector3()).x,
              boundingBox.getCenter(new THREE.Vector3()).y,
              boundingBox.getCenter(new THREE.Vector3()).z
            )}
            attach="position"
          />
        </mesh>
      )}

      {/* Model info */}
      <Text
        position={[0, boundingBox.getSize(new THREE.Vector3()).y / 2 + 5, 0]}
        fontSize={2}
        color="#333333"
        anchorX="center"
        anchorY="middle"
      >
        {model.name}
      </Text>
    </group>
  );
};

// Scene setup component
interface SceneSetupProps {
  settings: ViewportSettings;
  showStats: boolean;
  showGrid: boolean;
}

const SceneSetup: React.FC<SceneSetupProps> = ({ settings, showStats, showGrid }) => {
  const { camera } = useThree();

  useEffect(() => {
    // Update camera settings
    camera.position.set(
      settings.camera.position.x,
      settings.camera.position.y,
      settings.camera.position.z
    );
    camera.fov = settings.camera.fov;
    camera.near = settings.camera.near;
    camera.far = settings.camera.far;
    camera.updateProjectionMatrix();
  }, [camera, settings.camera]);

  return (
    <>
      {/* Lighting */}
      {settings.environment.lighting === 'studio' && (
        <>
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[10, 10, 5]}
            intensity={1}
            castShadow
            shadow-mapSize={[1024, 1024]}
            shadow-camera-far={50}
            shadow-camera-left={-10}
            shadow-camera-right={10}
            shadow-camera-top={10}
            shadow-camera-bottom={-10}
          />
        </>
      )}

      {settings.environment.lighting === 'outdoor' && (
        <>
          <ambientLight intensity={0.6} />
          <directionalLight
            position={[-1, 1, 1]}
            intensity={1.2}
            castShadow
            shadow-mapSize={[1024, 1024]}
          />
          <pointLight position={[10, 10, 10]} intensity={0.5} />
        </>
      )}

      {/* Environment */}
      {settings.environment.background === 'hdri' && settings.environment.environmentMap && (
        <Environment files={settings.environment.environmentMap} />
      )}

      {/* Grid */}
      {showGrid && <Grid args={[20, 20]} />}

      {/* Stats */}
      {showStats && <Stats />}

      {/* Contact shadows for better depth perception */}
      <ContactShadows
        position={[0, -10, 0]}
        opacity={0.4}
        scale={40}
        blur={1}
        far={10}
        resolution={256}
        color="#000000"
      />
    </>
  );
};

// Main ThreeJS Viewer Component
interface ThreeJSViewerProps {
  model?: Model3D;
  settings?: Partial<ViewportSettings>;
  wireframe?: boolean;
  showStats?: boolean;
  showGrid?: boolean;
  showBoundingBox?: boolean;
  autoRotate?: boolean;
  className?: string;
  onError?: (error: Error) => void;
}

export const ThreeJSViewer: React.FC<ThreeJSViewerProps> = ({
  model,
  settings = {},
  wireframe = false,
  showStats = false,
  showGrid = true,
  showBoundingBox = false,
  autoRotate = false,
  className = '',
  onError
}) => {
  const defaultSettings: ViewportSettings = {
    camera: {
      position: { x: 5, y: 5, z: 5 },
      target: { x: 0, y: 0, z: 0 },
      up: { x: 0, y: 1, z: 0 },
      fov: 50,
      near: 0.1,
      far: 1000
    },
    renderer: {
      antialias: true,
      shadows: true,
      shadowMapType: 'pcf',
      toneMapping: 'aces',
      physicallyCorrectLights: true
    },
    controls: {
      enableZoom: true,
      enablePan: true,
      enableRotate: true,
      autoRotate,
      autoRotateSpeed: 2,
      damping: 0.05
    },
    environment: {
      background: 'color',
      backgroundColor: '#f0f0f0',
      lighting: 'studio'
    }
  };

  const finalSettings = { ...defaultSettings, ...settings };
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Handle errors
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('Three.js error:', event.error);
      onError?.(event.error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, [onError]);

  return (
    <div className={`w-full h-full relative bg-gray-100 ${className}`}>
      <Canvas
        ref={canvasRef}
        shadows={finalSettings.renderer.shadows}
        dpr={[1, 2]}
        camera={{ 
          position: [
            finalSettings.camera.position.x, 
            finalSettings.camera.position.y, 
            finalSettings.camera.position.z
          ],
          fov: finalSettings.camera.fov
        }}
        gl={{
          antialias: finalSettings.renderer.antialias,
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        <Suspense fallback={<Loader />}>
          <SceneSetup
            settings={finalSettings}
            showStats={showStats}
            showGrid={showGrid}
          />

          {/* Camera Controls */}
          <OrbitControls
            enableZoom={finalSettings.controls.enableZoom}
            enablePan={finalSettings.controls.enablePan}
            enableRotate={finalSettings.controls.enableRotate}
            autoRotate={finalSettings.controls.autoRotate}
            autoRotateSpeed={finalSettings.controls.autoRotateSpeed}
            dampingFactor={finalSettings.controls.damping}
            enableDamping
            minDistance={2}
            maxDistance={50}
          />

          {/* Render Model */}
          {model ? (
            <Model3DComponent
              model={model}
              wireframe={wireframe}
              showBoundingBox={showBoundingBox}
            />
          ) : (
            // Placeholder geometry when no model is loaded
            <mesh castShadow receiveShadow>
              <boxGeometry args={[2, 2, 2]} />
              <meshStandardMaterial color="#4A90E2" />
            </mesh>
          )}
        </Suspense>
      </Canvas>

      {/* Overlay info */}
      <AnimatePresence>
        {model && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm p-4 rounded-lg shadow-lg max-w-xs"
          >
            <h3 className="font-semibold text-gray-800">{model.name}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {model.metadata.vertexCount} vertices • {model.metadata.faceCount} faces
            </p>
            <div className="flex items-center mt-2 space-x-2">
              <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                {model.settings.resolution}
              </span>
              <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                {model.settings.fileFormat.toUpperCase()}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ThreeJSViewer;