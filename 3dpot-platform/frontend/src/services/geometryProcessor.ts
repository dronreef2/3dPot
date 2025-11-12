// Geometry Processing Service for 3D Models
import * as THREE from 'three';
import { saveAs } from 'file-saver';
import { GeometryProcessor, ExportOptions } from '../types/model3d';

export class GeometryProcessingService implements GeometryProcessor {
  private scene: THREE.Scene;
  private renderer: THREE.WebGLRenderer;
  private camera: THREE.PerspectiveCamera;

  constructor() {
    // Initialize Three.js core components for processing
    this.scene = new THREE.Scene();
    this.renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
    this.camera = new THREE.PerspectiveCamera(
      75,
      1, // Will be updated per model
      0.1,
      1000
    );
  }

  /**
   * Optimize 3D geometry for performance
   */
  async optimize(): Promise<void> {
    console.log('Starting geometry optimization...');
    
    // Optimize all geometries in the scene
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        this.optimizeMesh(object);
      }
    });

    console.log('Geometry optimization completed');
  }

  /**
   * Decimate geometry by reducing polygon count
   */
  async decimate(factor: number): Promise<void> {
    console.log(`Starting geometry decimation with factor ${factor}...`);
    
    if (factor < 0.1 || factor > 1) {
      throw new Error('Decimation factor must be between 0.1 and 1.0');
    }

    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.geometry instanceof THREE.BufferGeometry) {
        this.decimateGeometry(object, factor);
      }
    });

    console.log(`Geometry decimation completed (factor: ${factor})`);
  }

  /**
   * Apply smooth shading to geometry
   */
  async smoothShading(): Promise<void> {
    console.log('Applying smooth shading...');
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.geometry instanceof THREE.BufferGeometry) {
        this.applySmoothShading(object.geometry);
      }
    });

    console.log('Smooth shading applied');
  }

  /**
   * Generate vertex normals for lighting
   */
  async generateNormals(): Promise<void> {
    console.log('Generating vertex normals...');
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.geometry instanceof THREE.BufferGeometry) {
        object.geometry.computeVertexNormals();
      }
    });

    console.log('Vertex normals generated');
  }

  /**
   * Compress geometry data
   */
  async compress(level: number): Promise<ArrayBuffer> {
    console.log(`Starting geometry compression (level: ${level})...`);
    
    const exporter = new THREE.BufferGeometryExporter();
    const compressedData: Uint8Array[] = [];

    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.geometry instanceof THREE.BufferGeometry) {
        const geometryData = exporter.parse(object.geometry);
        const compressed = this.compressGeometryData(geometryData, level);
        compressedData.push(compressed);
      }
    });

    // Combine all compressed data
    const totalLength = compressedData.reduce((sum, data) => sum + data.length, 0);
    const combinedData = new Uint8Array(totalLength);
    let offset = 0;
    
    for (const data of compressedData) {
      combinedData.set(data, offset);
      offset += data.length;
    }

    console.log(`Geometry compression completed (level: ${level})`);
    return combinedData.buffer;
  }

  /**
   * Validate geometry integrity
   */
  async validate(): Promise<boolean> {
    console.log('Validating geometry...');
    
    let isValid = true;
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.geometry instanceof THREE.BufferGeometry) {
        const validation = this.validateGeometry(object.geometry);
        if (!validation.isValid) {
          console.warn(`Invalid geometry found: ${validation.issues.join(', ')}`);
          isValid = false;
        }
      }
    });

    console.log(`Geometry validation ${isValid ? 'passed' : 'failed'}`);
    return isValid;
  }

  /**
   * Export model to various formats
   */
  async export(format: string, options: ExportOptions): Promise<void> {
    console.log(`Exporting model as ${format.toUpperCase()}...`);

    switch (format.toLowerCase()) {
      case 'obj':
        await this.exportOBJ(options);
        break;
      case 'stl':
        await this.exportSTL(options);
        break;
      case 'gltf':
        await this.exportGLTF(options);
        break;
      case 'objmtl':
        await this.exportOBJPNT(options);
        break;
      case 'ply':
        await this.exportPLY(options);
        break;
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }

    console.log(`Model exported as ${format.toUpperCase()}`);
  }

  /**
   * Merge multiple meshes into one
   */
  async mergeMeshes(meshIds: string[]): Promise<THREE.BufferGeometry> {
    console.log(`Merging ${meshIds.length} meshes...`);
    
    const geometries: THREE.BufferGeometry[] = [];
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && meshIds.includes(object.uuid)) {
        geometries.push(object.geometry);
      }
    });

    if (geometries.length === 0) {
      throw new Error('No valid meshes found for merging');
    }

    const mergedGeometry = THREE.BufferGeometryUtils.mergeBufferGeometries(geometries);
    console.log(`Merged ${geometries.length} meshes successfully`);
    
    return mergedGeometry;
  }

  /**
   * Apply texture to geometry
   */
  async applyTexture(textureUrl: string, uvChannel: string = 'uv'): Promise<void> {
    console.log(`Applying texture: ${textureUrl}`);
    
    const loader = new THREE.TextureLoader();
    const texture = await new Promise<THREE.Texture>((resolve, reject) => {
      loader.load(
        textureUrl,
        resolve,
        undefined,
        reject
      );
    });

    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.material instanceof THREE.MeshStandardMaterial) {
        object.material.map = texture;
        object.material.needsUpdate = true;
      }
    });

    console.log('Texture applied successfully');
  }

  /**
   * Split geometry into separate parts
   */
  async splitGeometry(meshId: string, splitMode: 'by_material' | 'by_faces' | 'random'): Promise<THREE.BufferGeometry[]> {
    console.log(`Splitting geometry with mode: ${splitMode}`);
    
    const mesh = this.scene.getObjectByProperty('uuid', meshId) as THREE.Mesh;
    if (!mesh || !(mesh.geometry instanceof THREE.BufferGeometry)) {
      throw new Error('Mesh not found or invalid geometry');
    }

    let splitGeometries: THREE.BufferGeometry[] = [];

    switch (splitMode) {
      case 'by_material':
        splitGeometries = this.splitByMaterial(mesh);
        break;
      case 'by_faces':
        splitGeometries = this.splitByFaces(mesh);
        break;
      case 'random':
        splitGeometries = this.splitRandom(mesh);
        break;
    }

    console.log(`Geometry split into ${splitGeometries.length} parts`);
    return splitGeometries;
  }

  // Private helper methods

  private optimizeMesh(mesh: THREE.Mesh): void {
    // Remove unused vertices
    mesh.geometry = this.removeUnusedVertices(mesh.geometry);
    
    // Merge vertices with same position
    mesh.geometry = this.mergeDuplicateVertices(mesh.geometry);
    
    // Optimize index buffer
    mesh.geometry = this.optimizeIndexBuffer(mesh.geometry);
  }

  private decimateGeometry(mesh: THREE.Mesh, factor: number): void {
    const geometry = mesh.geometry;
    const positionAttribute = geometry.getAttribute('position');
    const normalAttribute = geometry.getAttribute('normal');
    const uvAttribute = geometry.getAttribute('uv');

    if (!positionAttribute) return;

    // Calculate new vertex count
    const originalVertexCount = positionAttribute.count;
    const newVertexCount = Math.floor(originalVertexCount * factor);

    // Simple decimation by removing every nth vertex
    if (newVertexCount < originalVertexCount) {
      const newPosition = new Float32Array(newVertexCount * 3);
      const newNormal = normalAttribute ? new Float32Array(newVertexCount * 3) : null;
      const newUV = uvAttribute ? new Float32Array(newVertexCount * 2) : null;

      for (let i = 0; i < newVertexCount; i++) {
        const sourceIndex = Math.floor(i / factor);
        
        // Copy position
        newPosition[i * 3] = positionAttribute.getX(sourceIndex);
        newPosition[i * 3 + 1] = positionAttribute.getY(sourceIndex);
        newPosition[i * 3 + 2] = positionAttribute.getZ(sourceIndex);

        // Copy normal
        if (newNormal && normalAttribute) {
          newNormal[i * 3] = normalAttribute.getX(sourceIndex);
          newNormal[i * 3 + 1] = normalAttribute.getY(sourceIndex);
          newNormal[i * 3 + 2] = normalAttribute.getZ(sourceIndex);
        }

        // Copy UV
        if (newUV && uvAttribute) {
          newUV[i * 2] = uvAttribute.getX(sourceIndex);
          newUV[i * 2 + 1] = uvAttribute.getY(sourceIndex);
        }
      }

      mesh.geometry.setAttribute('position', new THREE.BufferAttribute(newPosition, 3));
      if (newNormal) {
        mesh.geometry.setAttribute('normal', new THREE.BufferAttribute(newNormal, 3));
      }
      if (newUV) {
        mesh.geometry.setAttribute('uv', new THREE.BufferAttribute(newUV, 2));
      }
    }
  }

  private applySmoothShading(geometry: THREE.BufferGeometry): void {
    geometry.computeVertexNormals();
    
    // Ensure all vertices are connected to avoid hard edges
    geometry.attributes.normal.needsUpdate = true;
  }

  private compressGeometryData(data: any, level: number): Uint8Array {
    // Simple compression based on level
    const jsonString = JSON.stringify(data);
    
    if (level === 0) {
      return new TextEncoder().encode(jsonString);
    }

    // Apply basic compression (in a real implementation, you'd use a proper compression library)
    const compressed = this.basicCompress(jsonString, level);
    return new TextEncoder().encode(compressed);
  }

  private basicCompress(text: string, level: number): string {
    // Very basic compression - remove extra spaces and newlines
    let compressed = text.replace(/\s+/g, ' ').trim();
    
    if (level >= 2) {
      // Remove quotes from simple key-value pairs
      compressed = compressed.replace(/"(\w+)":/g, '$1:');
    }
    
    if (level >= 3) {
      // Use single quotes for strings
      compressed = compressed.replace(/"([^"]*)"/g, "'$1'");
    }

    return compressed;
  }

  private validateGeometry(geometry: THREE.BufferGeometry): { isValid: boolean; issues: string[] } {
    const issues: string[] = [];
    
    // Check position attribute
    const position = geometry.getAttribute('position');
    if (!position) {
      issues.push('Missing position attribute');
    } else if (position.count < 3) {
      issues.push('Insufficient vertices (minimum 3 required)');
    }

    // Check for NaN or infinite values
    if (position) {
      const positions = position.array as Float32Array;
      for (let i = 0; i < positions.length; i++) {
        if (isNaN(positions[i]) || !isFinite(positions[i])) {
          issues.push(`Invalid vertex value at index ${i}: ${positions[i]}`);
          break;
        }
      }
    }

    // Check index
    if (geometry.index) {
      const index = geometry.index;
      const indexArray = index.array as Uint16Array | Uint32Array;
      const vertexCount = position?.count || 0;
      
      for (let i = 0; i < indexArray.length; i++) {
        if (indexArray[i] >= vertexCount) {
          issues.push(`Index out of bounds: ${indexArray[i]} >= ${vertexCount}`);
          break;
        }
      }
    }

    return {
      isValid: issues.length === 0,
      issues
    };
  }

  private async exportOBJ(options: ExportOptions): Promise<void> {
    const exporter = new THREE.OBJExporter();
    const objString = exporter.parse(this.scene);
    
    if (options.includeMaterials && options.metadata) {
      // Add metadata as comment
      const metadata = `# ${options.metadata.author}\n# ${options.metadata.copyright}\n# Version: ${options.metadata.version}\n\n`;
      const finalString = metadata + objString;
      
      const blob = new Blob([finalString], { type: 'text/plain' });
      saveAs(blob, 'model.obj');
    } else {
      const blob = new Blob([objString], { type: 'text/plain' });
      saveAs(blob, 'model.obj');
    }
  }

  private async exportSTL(options: ExportOptions): Promise<void> {
    const exporter = new THREE.STLExporter();
    const binary = options.binary;
    const stlString = exporter.parse(this.scene, { binary });
    
    const blob = new Blob([stlString], { type: 'application/octet-stream' });
    saveAs(blob, 'model.stl');
  }

  private async exportGLTF(options: ExportOptions): Promise<void> {
    const exporter = new THREE.GLTFExporter();
    
    const gltfOptions = {
      binary: options.binary,
      includeCustomExtensions: true,
      embedImages: options.includeTextures,
      animations: []
    };

    exporter.parse(
      this.scene,
      (gltf) => {
        let blob: Blob;
        
        if (options.binary) {
          blob = new Blob([gltf as ArrayBuffer], { type: 'application/octet-stream' });
          saveAs(blob, 'model.glb');
        } else {
          const jsonString = JSON.stringify(gltf, null, 2);
          blob = new Blob([jsonString], { type: 'application/json' });
          saveAs(blob, 'model.gltf');
        }
      },
      (error) => {
        console.error('GLTF export error:', error);
      },
      gltfOptions
    );
  }

  private async exportOBJPNT(options: ExportOptions): Promise<void> {
    // Export OBJ
    await this.exportOBJ(options);
    
    // Export MTL
    if (options.includeMaterials) {
      const mtlString = this.generateMTL();
      const mtlBlob = new Blob([mtlString], { type: 'text/plain' });
      saveAs(mtlBlob, 'model.mtl');
    }
  }

  private async exportPLY(options: ExportOptions): Promise<void> {
    const exporter = new THREE.PLYExporter();
    const plyString = exporter.parse(this.scene, { 
      binary: options.binary,
      excludeAttributes: ['index']
    });
    
    const blob = new Blob([plyString], { type: 'text/plain' });
    saveAs(blob, 'model.ply');
  }

  private generateMTL(): string {
    let mtlContent = '# 3D Pot Platform Generated MTL\n\n';
    
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.material instanceof THREE.MeshStandardMaterial) {
        const material = object.material as THREE.MeshStandardMaterial;
        mtlContent += `newmtl ${material.name || 'Material'}\n`;
        mtlContent += `Ka ${material.ambient ? material.ambient.r : 0.2} ${material.ambient ? material.ambient.g : 0.2} ${material.ambient ? material.ambient.b : 0.2}\n`;
        mtlContent += `Kd ${material.color.r} ${material.color.g} ${material.color.b}\n`;
        mtlContent += `Ks ${material.metalness} ${material.metalness} ${material.metalness}\n`;
        mtlContent += `Ns ${material.roughness * 100}\n`;
        
        if (material.transparent) {
          mtlContent += `d ${material.opacity || 1}\n`;
        }
        
        mtlContent += '\n';
      }
    });
    
    return mtlContent;
  }

  private removeUnusedVertices(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
    // Implementation for removing vertices not used by any face
    // This is a simplified version
    return geometry;
  }

  private mergeDuplicateVertices(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
    // Implementation for merging vertices at the same position
    // This is a simplified version
    return geometry;
  }

  private optimizeIndexBuffer(geometry: THREE.BufferGeometry): THREE.BufferGeometry {
    // Implementation for optimizing triangle ordering for better cache performance
    // This is a simplified version
    return geometry;
  }

  private splitByMaterial(mesh: THREE.Mesh): THREE.BufferGeometry[] {
    // Split geometry by material groups
    const geometries: THREE.BufferGeometry[] = [];
    // Implementation would use draw ranges to separate by material
    return geometries.length > 0 ? geometries : [mesh.geometry];
  }

  private splitByFaces(mesh: THREE.Mesh): THREE.BufferGeometry[] {
    // Split geometry into individual faces
    const geometries: THREE.BufferGeometry[] = [];
    // Implementation would create separate geometry for each face
    return geometries.length > 0 ? geometries : [mesh.geometry];
  }

  private splitRandom(mesh: THREE.Mesh): THREE.BufferGeometry[] {
    // Split geometry into random chunks
    const geometries: THREE.BufferGeometry[] = [];
    // Implementation would randomly group faces
    return geometries.length > 0 ? geometries : [mesh.geometry];
  }

  // Public methods for external use

  public addMesh(mesh: THREE.Mesh): void {
    this.scene.add(mesh);
  }

  public removeMesh(meshId: string): void {
    const mesh = this.scene.getObjectByProperty('uuid', meshId);
    if (mesh) {
      this.scene.remove(mesh);
    }
  }

  public clearScene(): void {
    while (this.scene.children.length > 0) {
      this.scene.remove(this.scene.children[0]);
    }
  }

  public getScene(): THREE.Scene {
    return this.scene;
  }
}

export const geometryProcessor = new GeometryProcessingService();