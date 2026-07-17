ObjC.import('Foundation');
ObjC.import('PDFKit');

function fail(message) {
    throw new Error(message);
}

function parsePageRange(value, pageCount) {
    const trimmed = value.replace(/\s/g, '');
    if (!trimmed) fail('未填写页码范围');

    const pages = [];
    for (const component of trimmed.split(',')) {
        const match = component.match(/^(\d+)(?:-(\d+))?$/);
        if (!match) fail(`无效页码范围：${component}`);

        const first = Number(match[1]);
        const last = match[2] ? Number(match[2]) : first;
        if (first < 1 || last < first || last > pageCount) {
            fail(`页码超出范围：${component}（PDF 共 ${pageCount} 页）`);
        }
        for (let page = first; page <= last; page += 1) pages.push(page);
    }
    return pages;
}

function run(argv) {
    if (argv.length !== 3) fail('缺少 PDF、页码范围或输出路径');

    const inputURL = $.NSURL.fileURLWithPath(argv[0]);
    const outputURL = $.NSURL.fileURLWithPath(argv[2]);
    const source = $.PDFDocument.alloc.initWithURL(inputURL);
    if (!source) fail('无法读取 PDF');
    if (source.isLocked) fail('PDF 已加密，无法提取');

    const pages = parsePageRange(argv[1], source.pageCount);
    const result = $.PDFDocument.alloc.init;
    pages.forEach((pageNumber, index) => {
        const page = source.pageAtIndex(pageNumber - 1);
        if (!page) fail(`无法读取第 ${pageNumber} 页`);
        result.insertPageAtIndex(page, index);
    });
    if (!result.writeToURL(outputURL)) fail('无法写入输出文件');
}
