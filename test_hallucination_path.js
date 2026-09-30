const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
    constructor() {
        this.children = [];
        this.events = {};
        this.classList = { add() {}, toggle() {} };
        this.disabled = false;
        this.textContent = '';
        this.value = '';
    }

    set innerHTML(value) {
        this.children = [];
        this._innerHTML = value;
    }

    get innerHTML() { return this._innerHTML; }
    append(...children) { this.children.push(...children); }
    appendChild(child) { this.children.push(child); }
    addEventListener(name, handler) { this.events[name] = handler; }
    setAttribute() {}
}

const elements = new Map([
    ['path-prompt-input', new Element()],
    ['path-start-btn', new Element()],
    ['finish-path-btn', new Element()],
    ['path-candidates', new Element()],
    ['path-tree', new Element()],
    ['active-premise-label', new Element()],
    ['active-premise-text', new Element()],
    ['active-response-label', new Element()],
    ['active-response-text', new Element()],
    ['path-status', new Element()],
]);
global.document = {
    body: { dataset: { staticDemo: 'false' } },
    getElementById(id) { return elements.get(id); },
    createElement() { return new Element(); },
    addEventListener() {},
};
global.window = { i18n: { t: (key) => key, getLocale: () => 'en' } };

const initialSegment = [
    { selected_token: ' A', selected_prob: 0.8, top_logprobs: [{ token: ' A', probability: 0.8 }, { token: ' alt', probability: 0.1 }] },
    { selected_token: ' B', selected_prob: 0.7, top_logprobs: [{ token: ' B', probability: 0.7 }] },
];
const branchSegment = [
    { selected_token: ' branch', selected_prob: 0.75, top_logprobs: [{ token: ' branch', probability: 0.75 }] },
];
const calls = [];
global.fetch = async (_url, options) => {
    const payload = JSON.parse(options.body);
    calls.push(payload);
    return {
        ok: true,
        json: async () => ({ tokenProbs: payload.response_prefix ? branchSegment : initialSegment }),
    };
};

vm.runInThisContext(fs.readFileSync('static/hallucination-path.js', 'utf8'));

async function clickCandidate(index) {
    await elements.get('path-candidates').children[index].events.click();
}

(async () => {
    const input = elements.get('path-prompt-input');
    input.value = 'False premise';
    await elements.get('path-start-btn').events.click();
    assert.equal(calls.length, 1);
    assert.equal(calls[0].response_prefix, '');
    assert.equal(elements.get('active-premise-text').textContent, 'False premise');
    assert.equal(elements.get('active-response-text').textContent, 'pathResponseEmpty');

    await clickCandidate(0);
    assert.equal(calls.length, 1, 'following the selected token must not fetch');
    assert.equal(elements.get('active-premise-text').textContent, 'False premise');
    assert.equal(elements.get('active-response-text').textContent, ' A');
    await clickCandidate(0);
    assert.equal(calls.length, 1, 'revealing the final selected token must not fetch');
    assert.equal(elements.get('path-candidates').textContent, 'pathComplete');

    await elements.get('path-start-btn').events.click();
    await clickCandidate(1);
    assert.equal(calls.length, 3, 'an alternative must fetch one branch segment');
    assert.equal(calls[2].response_prefix, ' alt');
    assert.equal(elements.get('path-candidates').children[0].children[0].textContent, '␠branch');
})().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
