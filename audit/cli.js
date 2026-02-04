#!/usr/bin/env node

/**
 * Speed Audit CLI
 * Command line interface for performance auditing
 */

import { SpeedAudit } from './audit.js';
import { writeFile } from 'fs/promises';
import { program } from 'commander';

program
  .name('speed-audit')
  .description('Comprehensive website performance analysis tool')
  .version('1.0.0');

program
  .argument('<url>', 'Website URL to audit')
  .option('-d, --detailed', 'Generate detailed HTML report')
  .option('-o, --output <file>', 'Output file for report')
  .option('-c, --competitors <urls>', 'Comma-separated list of competitor URLs')
  .option('-t, --timeout <ms>', 'Request timeout in milliseconds', '30000')
  .option('-q, --quiet', 'Suppress output except for errors')
  .option('--json', 'Output results as JSON');

program.parse();

const options = program.opts();
const url = program.args[0];

if (!url) {
  console.error('Error: URL is required');
  process.exit(1);
}

async function main() {
  try {
    const auditOptions = {
      timeout: parseInt(options.timeout),
      competitors: options.competitors ? options.competitors.split(',') : []
    };

    const audit = new SpeedAudit(auditOptions);
    
    if (!options.quiet) {
      console.log(`🚀 Starting speed audit for: ${url}`);
      if (auditOptions.competitors.length > 0) {
        console.log(`📊 Analyzing competitors: ${auditOptions.competitors.join(', ')}`);
      }
    }

    const results = await audit.analyze(url);

    if (options.json) {
      console.log(JSON.stringify(results, null, 2));
      return;
    }

    // Display results
    console.log(`\n📊 Performance Score: ${results.score}/100`);
    console.log(`⚡ Load Time: ${Math.round(results.performance.loadTime / 1000)}s`);
    console.log(`🌐 TTFB: ${results.performance.ttfb}ms`);
    console.log(`📦 Page Size: ${Math.round(results.performance.contentSize / 1024 / 1024)}MB`);

    if (results.recommendations.length > 0) {
      console.log(`\n💡 Recommendations (${results.recommendations.length}):`);
      results.recommendations.slice(0, 5).forEach((rec, index) => {
        const icon = rec.type === 'critical' ? '🚨' : rec.type === 'warning' ? '⚠️' : '💡';
        console.log(`${icon} ${index + 1}. ${rec.title}`);
        console.log(`   ${rec.description}`);
        console.log(`   Impact: ${rec.impact} | Effort: ${rec.effort} | Savings: ${rec.savings}\n`);
      });

      if (results.recommendations.length > 5) {
        console.log(`... and ${results.recommendations.length - 5} more recommendations`);
      }
    }

    // Competitive analysis
    if (results.competitive && results.competitive.competitors.length > 0) {
      console.log(`\n🏆 Competitive Analysis:`);
      results.competitive.competitors.forEach((competitor, index) => {
        console.log(`${index + 1}. ${competitor.url}`);
        console.log(`   Score: ${competitor.score}/100 | Load Time: ${Math.round(competitor.loadTime / 1000)}s`);
      });
    }

    // Generate detailed report if requested
    if (options.detailed || options.output) {
      const html = audit.generateHTMLReport(results);
      const outputFile = options.output || `speed-audit-${Date.now()}.html`;
      await writeFile(outputFile, html);
      console.log(`\n📄 Detailed report saved to: ${outputFile}`);
    }

    // Exit with appropriate code
    process.exit(results.score >= 60 ? 0 : 1);

  } catch (error) {
    console.error(`❌ Audit failed: ${error.message}`);
    process.exit(1);
  }
}

main().catch(console.error);