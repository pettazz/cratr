import classificationDefs from '../../../classifier-definitions.json';

const classificationMap = new Map(classificationDefs.map(cls => [cls.id, cls]));

const resourceSet = new Set();      
classificationDefs.map(cls => cls.resources.forEach(r => resourceSet.add(r)));
const resourceList = [...resourceSet];

export { classificationMap, resourceList };