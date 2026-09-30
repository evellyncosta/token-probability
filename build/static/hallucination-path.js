(() => {
    const state = { nodes: new Map(), activeNodeId: null, nextId: 0 };
    const isStaticDemo = document.body.dataset.staticDemo === 'true';
    const input = document.getElementById('path-prompt-input');
    const startButton = document.getElementById('path-start-btn');
    const finishButton = document.getElementById('finish-path-btn');
    const candidatesElement = document.getElementById('path-candidates');
    const treeElement = document.getElementById('path-tree');
    const activePathElement = document.getElementById('active-path-text');
    const statusElement = document.getElementById('path-status');

    function t(key) {
        return window.i18n.t(key);
    }

    function formatToken(token) {
        return token.replace(/ /g, '␠').replace(/\n/g, '↵').replace(/\t/g, '⇥');
    }

    function createNode({ parentId = null, token = '', probability = null, context, candidates = [] }) {
        const id = `path-node-${state.nextId++}`;
        const node = { id, parentId, token, probability, context, candidates, children: [] };
        state.nodes.set(id, node);
        if (parentId) state.nodes.get(parentId).children.push(id);
        return node;
    }

    function activeNode() {
        return state.nodes.get(state.activeNodeId);
    }

    function candidateChoices(tokenData) {
        const candidates = [...(tokenData.top_logprobs || [])];
        if (!candidates.some((candidate) => candidate.token === tokenData.selected_token)) {
            candidates.unshift({ token: tokenData.selected_token, probability: tokenData.selected_prob });
        }
        return candidates.filter((candidate, index, all) => (
            all.findIndex((other) => other.token === candidate.token) === index
        ));
    }

    function activePath() {
        const nodes = [];
        let node = activeNode();
        while (node) {
            nodes.unshift(node);
            node = node.parentId ? state.nodes.get(node.parentId) : null;
        }
        return nodes;
    }

    function renderActivePath() {
        const node = activeNode();
        activePathElement.textContent = node ? node.context : t('pathEmpty');
        finishButton.disabled = !node;
    }

    function renderCandidates() {
        candidatesElement.innerHTML = '';
        const node = activeNode();
        if (!node || !node.candidates.length) {
            if (node) candidatesElement.textContent = t('noCandidates');
            return;
        }
        node.candidates.forEach((candidate) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'path-candidate';
            button.innerHTML = '';
            const token = document.createElement('span');
            token.className = 'path-candidate-token';
            token.textContent = formatToken(candidate.token);
            const probability = document.createElement('span');
            probability.className = 'path-candidate-probability';
            probability.textContent = `${(candidate.probability * 100).toFixed(1)}%`;
            button.append(token, probability);
            button.addEventListener('click', () => chooseCandidate(candidate));
            candidatesElement.appendChild(button);
        });
    }

    function renderTreeNode(node, parent) {
        const item = document.createElement('li');
        item.className = 'path-tree-item';
        item.setAttribute('role', 'treeitem');
        item.setAttribute('aria-selected', String(node.id === state.activeNodeId));
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'path-tree-node';
        if (node.id === state.activeNodeId) button.classList.add('path-tree-node-active');
        const token = document.createElement('span');
        token.textContent = node.parentId ? formatToken(node.token) : node.context;
        button.appendChild(token);
        if (node.probability !== null) {
            const probability = document.createElement('small');
            probability.textContent = ` ${(node.probability * 100).toFixed(1)}%`;
            button.appendChild(probability);
        }
        button.addEventListener('click', () => selectNode(node.id));
        item.appendChild(button);
        if (node.children.length) {
            const children = document.createElement('ul');
            children.setAttribute('role', 'group');
            node.children.forEach((childId) => renderTreeNode(state.nodes.get(childId), children));
            item.appendChild(children);
        }
        parent.appendChild(item);
    }

    function renderTree() {
        treeElement.innerHTML = '';
        const root = [...state.nodes.values()].find((node) => node.parentId === null);
        if (!root) return;
        const list = document.createElement('ul');
        list.className = 'path-tree-list';
        renderTreeNode(root, list);
        treeElement.appendChild(list);
    }

    function render() {
        renderActivePath();
        renderCandidates();
        renderTree();
    }

    function setLoading(isLoading) {
        startButton.disabled = isLoading;
        candidatesElement.classList.toggle('path-candidates-loading', isLoading);
        if (isLoading) candidatesElement.textContent = t('loadingChoices');
    }

    async function requestCandidates(context) {
        if (isStaticDemo) {
            return {
                selected_token: ' it', selected_prob: 0.72,
                top_logprobs: [
                    { token: ' it', probability: 0.72 },
                    { token: ' Sydney', probability: 0.15 },
                    { token: ' the', probability: 0.08 },
                ],
            };
        }
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: context,
                top_k: 5,
                temperature: 0.0,
                mode: 'path',
                locale: window.i18n.getLocale(),
            }),
        });
        if (!response.ok) throw new Error('Could not generate next-token candidates.');
        const data = await response.json();
        if (!data.tokenProbs || data.tokenProbs.length !== 1) {
            throw new Error('The next-token response was invalid.');
        }
        return data.tokenProbs[0];
    }

    async function loadCandidates(node) {
        setLoading(true);
        statusElement.textContent = '';
        try {
            node.candidates = candidateChoices(await requestCandidates(node.context));
            render();
        } catch (error) {
            node.candidates = [];
            candidatesElement.textContent = t('noCandidates');
            statusElement.textContent = t('generationError');
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    async function startPath() {
        const premise = input.value;
        if (!premise.trim()) {
            statusElement.textContent = t('enterFalsePremise');
            input.focus();
            return;
        }
        state.nodes.clear();
        state.nextId = 0;
        const root = createNode({ context: premise });
        state.activeNodeId = root.id;
        input.disabled = true;
        render();
        await loadCandidates(root);
    }

    async function chooseCandidate(candidate) {
        const parent = activeNode();
        if (!parent) return;
        const child = createNode({
            parentId: parent.id,
            token: candidate.token,
            probability: candidate.probability,
            context: parent.context + candidate.token,
        });
        state.activeNodeId = child.id;
        render();
        await loadCandidates(child);
    }

    function selectNode(nodeId) {
        state.activeNodeId = nodeId;
        statusElement.textContent = '';
        render();
    }

    startButton.addEventListener('click', startPath);
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            startPath();
        }
    });
    finishButton.addEventListener('click', () => {
        statusElement.textContent = t('pathFinished');
    });
    document.addEventListener('localechange', render);
})();
