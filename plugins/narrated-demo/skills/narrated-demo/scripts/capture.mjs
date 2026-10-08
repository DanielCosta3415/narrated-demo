// Uses the vendored Cutaway API, not invented CLI flags.
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [plan, output, deps, locale='pt-BR'] = process.argv.slice(2);
if (!plan || !output || !deps) throw new Error('Expected PLAN OUTPUT NODE_RUNTIME [LOCALE]');
if (!/^[a-z]{2}(-[A-Z]{2})?$/.test(locale)) throw new Error('Invalid locale');
process.env.NARRATED_DEMO_NODE_DEPS=resolve(deps);
process.env.NARRATED_DEMO_LOCALE=locale;
const {record}=await import('./cutaway/capture/record.mjs');
await record(resolve(plan),resolve(output));
