"""
Reusable UI components for the AI Knowledge Hub.

Premium warm aesthetic with Three.js 3D background,
serif typography, and vellum-glass panels.
"""
import streamlit as st
import streamlit.components.v1 as stc


def render_3d_hero():
    """Render the full hero section with interactive Three.js particle sphere."""
    stc.html("""
    <div id="hero-wrapper" style="
        position: relative;
        width: 100%;
        height: 560px;
        overflow: hidden;
        background: #FDFCF8;
        border-bottom: 1px solid rgba(28, 25, 23, 0.06);
    ">
        <!-- Three.js Canvas -->
        <canvas id="hero-canvas" style="position:absolute;inset:0;width:100%;height:100%;z-index:0;"></canvas>

        <!-- Grid Overlay -->
        <div style="
            position: absolute; inset: 0; z-index: 1; pointer-events: none;
            background-size: 40px 40px;
            background-image:
                linear-gradient(to right, rgba(28,25,23,0.025) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(28,25,23,0.025) 1px, transparent 1px);
        ">
            <div style="position:absolute;inset:0;background:linear-gradient(to bottom, transparent 30%, rgba(253,252,248,0.4) 70%, #FDFCF8);"></div>
        </div>

        <!-- Text Content -->
        <div style="
            position: relative; z-index: 10;
            padding: 80px 50px 50px;
            max-width: 650px;
            animation: heroFadeIn 1.2s ease-out forwards;
            opacity: 0;
        ">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:28px;">
                <div style="height:1px;width:40px;background:#9A3412;"></div>
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#9A3412;text-transform:uppercase;letter-spacing:0.15em;">
                    RAG &middot; MULTI-MODEL &middot; AGENT MODE
                </span>
            </div>

            <h1 style="
                font-family: 'Cormorant Garamond', serif;
                font-size: 4.2rem;
                font-weight: 400;
                color: #1C1917;
                line-height: 1.0;
                letter-spacing: -0.02em;
                margin: 0;
                mix-blend-mode: multiply;
            ">
                AI Knowledge Hub
            </h1>
            <h1 style="
                font-family: 'Cormorant Garamond', serif;
                font-size: 4.2rem;
                font-weight: 300;
                font-style: italic;
                color: #78716C;
                line-height: 1.0;
                letter-spacing: -0.02em;
                margin: 0;
            ">
                Intelligent Documents
            </h1>

            <p style="
                margin-top: 32px;
                max-width: 440px;
                font-family: 'Inter', sans-serif;
                font-size: 0.95rem;
                font-weight: 300;
                color: #57534E;
                line-height: 1.75;
            ">
                Upload any document, ask questions, and get AI-powered answers
                grounded in your data — with full transparency into retrieval,
                routing, and reasoning.
            </p>

            <div style="margin-top:40px;display:flex;align-items:center;gap:20px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:7px;height:7px;border-radius:50%;background:#16a34a;box-shadow:0 0 10px rgba(22,163,74,0.5);animation:livePulse 2s ease-in-out infinite;"></div>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#57534E;text-transform:uppercase;letter-spacing:0.1em;">
                        CUSTOM RAG PIPELINE
                    </span>
                </div>
                <div style="height:1px;width:28px;background:#D6D3D1;"></div>
                <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.15rem;color:#78716C;letter-spacing:-0.01em;">
                    No LangChain — Built from Scratch
                </span>
            </div>

            <div style="margin-top:48px;display:flex;flex-direction:column;gap:3px;opacity:0.45;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#78716C;text-transform:uppercase;letter-spacing:0.15em;">
                    SECTOR: AI ENGINEERING
                </span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#78716C;text-transform:uppercase;letter-spacing:0.15em;">
                    PLATFORM: KNOWLEDGE HUB
                </span>
            </div>
        </div>

        <!-- Interactive Tech Panel (right side) -->
        <div id="tech-panel" style="
            position: absolute;
            bottom: 40px;
            right: 40px;
            width: 260px;
            background: rgba(253,252,248,0.88);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(28,25,23,0.08);
            z-index: 10;
            animation: heroFadeIn 1.2s ease-out 0.5s forwards;
            opacity: 0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 20px 40px -4px rgba(28,25,23,0.05);
            cursor: default;
        ">
            <!-- Header -->
            <div style="border-bottom:1px solid rgba(28,25,23,0.06);padding:14px 20px;display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.4);">
                <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.1rem;color:#1C1917;">Pipeline Engine</span>
            </div>

            <div style="padding:20px;">
                <!-- Slider 1: Distortion / Retrieval Depth -->
                <div style="margin-bottom:20px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;">RETRIEVAL DEPTH</span>
                        <span id="val-distortion" style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#A8A29E;">0.9</span>
                    </div>
                    <input type="range" id="input-distortion" min="0" max="2.0" step="0.1" value="0.9" style="
                        -webkit-appearance:none;width:100%;background:transparent;cursor:pointer;">
                </div>

                <!-- Slider 2: Size / Generation -->
                <div style="margin-bottom:20px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;">GENERATION</span>
                        <span id="val-size" style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#A8A29E;">2.4</span>
                    </div>
                    <input type="range" id="input-size" min="0.5" max="5.0" step="0.1" value="2.4" style="
                        -webkit-appearance:none;width:100%;background:transparent;cursor:pointer;">
                </div>

                <!-- Status bars -->
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;padding-top:16px;border-top:1px solid rgba(28,25,23,0.06);">
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">EMBED</div>
                        <div style="height:2px;width:100%;background:#E7E5E4;overflow:hidden;border-radius:1px;">
                            <div id="bar-embed" style="height:100%;width:85%;background:#1C1917;transition:width 0.5s ease;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">SEARCH</div>
                        <div style="height:2px;width:100%;background:#E7E5E4;overflow:hidden;border-radius:1px;">
                            <div id="bar-search" style="height:100%;width:92%;background:#1C1917;transition:width 0.5s ease;"></div>
                        </div>
                    </div>
                </div>

                <!-- Live status -->
                <div style="display:flex;justify-content:space-between;align-items:center;padding-top:16px;margin-top:16px;border-top:1px solid rgba(28,25,23,0.06);">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em;">AI LAYER</span>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:rgba(22,163,74,0.8);letter-spacing:0.1em;">LIVE</span>
                        <div style="width:7px;height:7px;border-radius:50%;background:#16a34a;box-shadow:0 0 10px rgba(22,163,74,0.5);animation:livePulse 2s ease-in-out infinite;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@200;300;400&family=JetBrains+Mono:wght@200;300;400&display=swap');

        @keyframes heroFadeIn {
            from { opacity: 0; transform: translateY(14px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes livePulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.35; }
        }

        /* Range slider styling */
        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none; height: 12px; width: 12px;
            background: #1C1917; border: 1px solid #FDFCF8;
            cursor: pointer; margin-top: -5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            border-radius: 0;
        }
        input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.25); }
        input[type=range]::-webkit-slider-runnable-track {
            width: 100%; height: 1px; cursor: pointer; background: #D6D3D1;
        }
        input[type=range]:focus { outline: none; }
    </style>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    (function() {
        const canvas = document.getElementById('hero-canvas');
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0xFDFCF8, 0.03);

        const camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
        camera.position.set(0, 0, 18);

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setClearColor(0xFDFCF8, 1);

        const group = new THREE.Group();
        group.position.set(5.5, 0.5, -2);
        scene.add(group);

        // Particle sphere
        const baseGeo = new THREE.IcosahedronGeometry(5.0, 28);
        const positions = baseGeo.attributes.position;
        const count = positions.count;

        const pGeo = new THREE.BufferGeometry();
        pGeo.setAttribute('position', new THREE.BufferAttribute(
            new Float32Array(positions.array), 3
        ));

        const pMat = new THREE.PointsMaterial({
            color: 0x1C1917,
            size: 0.04,
            transparent: true,
            opacity: 0.55,
            sizeAttenuation: true,
        });

        const particles = new THREE.Points(pGeo, pMat);
        group.add(particles);

        // Orbit rings
        function addOrbit(radius, rotX, rotY, opacity) {
            const curve = new THREE.EllipseCurve(0, 0, radius, radius, 0, Math.PI * 2, false);
            const pts = curve.getPoints(128);
            const oGeo = new THREE.BufferGeometry().setFromPoints(pts);
            const oMat = new THREE.LineBasicMaterial({ color: 0x78350F, transparent: true, opacity: opacity });
            const orbit = new THREE.Line(oGeo, oMat);
            orbit.rotation.x = rotX;
            orbit.rotation.y = rotY;
            group.add(orbit);
            return orbit;
        }

        const o1 = addOrbit(6.0, Math.PI/2, 0, 0.1);
        const o2 = addOrbit(5.6, Math.PI/3, Math.PI/6, 0.07);
        const o3 = addOrbit(6.5, Math.PI/1.8, Math.PI/4, 0.05);

        let t = 0;
        let mx = 0, my = 0;
        let distortion = 0.9;
        let particleSize = 2.4;

        // Mouse interaction
        canvas.parentElement.addEventListener('mousemove', (e) => {
            const rect = canvas.parentElement.getBoundingClientRect();
            mx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            my = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        });

        // Slider bindings — control the 3D sphere
        const distInput = document.getElementById('input-distortion');
        const sizeInput = document.getElementById('input-size');

        distInput.addEventListener('input', (e) => {
            distortion = parseFloat(e.target.value);
            document.getElementById('val-distortion').textContent = e.target.value;
            // Update status bars based on slider
            document.getElementById('bar-embed').style.width = Math.min(98, distortion * 50 + 40) + '%';
        });

        sizeInput.addEventListener('input', (e) => {
            particleSize = parseFloat(e.target.value);
            document.getElementById('val-size').textContent = e.target.value;
            pMat.size = particleSize * 0.018;
            document.getElementById('bar-search').style.width = Math.min(98, particleSize * 12 + 40) + '%';
        });

        function animate() {
            requestAnimationFrame(animate);
            t += 0.006;

            group.rotation.y = t * 0.12;
            group.rotation.z = Math.sin(t * 0.25) * 0.04;

            // Vertex animation controlled by distortion slider
            const pos = pGeo.attributes.position;
            const orig = baseGeo.attributes.position;
            for (let i = 0; i < count; i++) {
                const ox = orig.getX(i), oy = orig.getY(i), oz = orig.getZ(i);
                const noise = Math.sin(ox * 1.5 + t * 1.2) * Math.cos(oy * 1.5 + t * 0.8) * Math.sin(oz * 1.5 + t * 0.5);
                const len = Math.sqrt(ox*ox + oy*oy + oz*oz);
                const scale = (len + noise * distortion * 0.4) / len;
                pos.setXYZ(i, ox * scale, oy * scale, oz * scale);
            }
            pos.needsUpdate = true;

            o1.rotation.z += 0.0015;
            o2.rotation.z += 0.002;
            o3.rotation.z += 0.001;

            // Smooth camera follow mouse
            camera.position.x += (mx * 0.5 - camera.position.x) * 0.025;
            camera.position.y += (my * 0.4 - camera.position.y) * 0.025;
            camera.lookAt(0, 0, 0);

            renderer.render(scene, camera);
        }
        animate();

        // Resize handler
        window.addEventListener('resize', () => {
            camera.aspect = canvas.clientWidth / canvas.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        });
    })();
    </script>
    """, height=560)


def render_header():
    """Render just the text header (fallback)."""
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 1rem 2rem;border-bottom:1px solid rgba(28,25,23,0.06);margin-bottom:1.5rem;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;color:#1C1917;margin:0;letter-spacing:-0.02em;">
            AI Knowledge Hub
        </h1>
        <p style="font-family:'Inter',sans-serif;font-weight:300;font-size:0.95rem;color:#78716C;margin:0.6rem 0 0;">
            Intelligent Document Analysis with RAG, Multi-Model Routing &amp; Agent Mode
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value, col=None):
    """Render a styled metric card."""
    target = col or st
    target.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_source_badges(sources: list[str]):
    """Render source document badges."""
    badges = " ".join(f'<span class="source-badge">{s}</span>' for s in sources)
    st.markdown(f"<div style='margin:0.4rem 0;'>{badges}</div>", unsafe_allow_html=True)


def render_routing_badge(tier: str, model_name: str, reason: str):
    """Render the model routing indicator."""
    st.markdown(f"""
    <div class="routing-badge {tier}">
        {model_name} &middot; {reason}
    </div>
    """, unsafe_allow_html=True)


def render_agent_step(step_num: int, action: str, description: str, status: str = "running"):
    """Render an agent reasoning step."""
    icons = {"planning": "&#9672;", "searching": "&#9678;", "synthesizing": "&#9670;"}
    icon = icons.get(action, "&#9679;")
    st.markdown(f"""
    <div class="agent-step {status}">
        <strong>{icon} Step {step_num}:</strong> {description}
    </div>
    """, unsafe_allow_html=True)


def render_arch_card(number: str, title: str, body: str, col=None):
    """Render an architecture feature card."""
    target = col or st
    target.markdown(f"""
    <div class="arch-card">
        <div class="card-number">{number}</div>
        <div class="card-title">{title}</div>
        <div class="card-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def render_section_label(text: str):
    """Render a section label in the mono style."""
    st.markdown(f"""
    <div style="margin:2.5rem 0 1.5rem;display:flex;align-items:center;gap:12px;">
        <div style="height:1px;width:35px;background:#D6D3D1;"></div>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#A8A29E;
               text-transform:uppercase;letter-spacing:0.12em;">{text}</span>
    </div>
    """, unsafe_allow_html=True)
