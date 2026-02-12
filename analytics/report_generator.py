import json
from datetime import datetime
from html import escape


class ReportGenerator:
    """Professional engineering report generator supporting multiple report types."""

    REPORT_CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; color: #2c3e50; font-size: 11pt; line-height: 1.5; }
        .page { padding: 30px 40px; }

        /* Header */
        .report-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #2c3e50; padding-bottom: 15px; margin-bottom: 25px; }
        .header-left { flex: 1; }
        .header-right { text-align: right; font-size: 9pt; color: #7f8c8d; }
        .report-title { font-size: 20pt; font-weight: 700; color: #2c3e50; margin-bottom: 4px; }
        .report-subtitle { font-size: 11pt; color: #7f8c8d; }
        .report-id { font-size: 9pt; color: #95a5a6; font-family: monospace; }

        /* Metadata table */
        .meta-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .meta-table td { padding: 6px 12px; border: 1px solid #dce1e7; font-size: 10pt; }
        .meta-table td:first-child { background: #f7f9fc; font-weight: 600; width: 180px; color: #34495e; }

        /* Sections */
        .section { margin-bottom: 22px; page-break-inside: avoid; }
        .section-title { font-size: 13pt; font-weight: 700; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-bottom: 12px; }
        .subsection-title { font-size: 11pt; font-weight: 600; color: #34495e; margin: 10px 0 6px 0; }

        /* Data tables */
        .data-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 10pt; }
        .data-table th { background: #2c3e50; color: white; padding: 8px 12px; text-align: left; font-weight: 600; }
        .data-table td { padding: 7px 12px; border-bottom: 1px solid #ecf0f1; }
        .data-table tr:nth-child(even) { background: #f7f9fc; }
        .data-table tr:hover { background: #edf2f7; }

        /* Result cards */
        .result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin: 10px 0; }
        .result-card { background: #f7f9fc; border: 1px solid #dce1e7; border-radius: 6px; padding: 12px; text-align: center; }
        .result-card .label { font-size: 9pt; color: #7f8c8d; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .result-card .value { font-size: 16pt; font-weight: 700; color: #2c3e50; }
        .result-card .unit { font-size: 9pt; color: #95a5a6; }

        /* Compliance badges */
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 9pt; font-weight: 600; }
        .badge-pass { background: #d5f5e3; color: #27ae60; }
        .badge-fail { background: #fadbd8; color: #e74c3c; }
        .badge-warn { background: #fdebd0; color: #f39c12; }
        .badge-info { background: #d6eaf8; color: #2980b9; }

        /* Steps / workflow */
        .step-list { list-style: none; padding: 0; counter-reset: step-counter; }
        .step-item { position: relative; padding: 10px 12px 10px 50px; margin-bottom: 8px; background: #f7f9fc; border-radius: 6px; border-left: 3px solid #3498db; counter-increment: step-counter; }
        .step-item::before { content: counter(step-counter); position: absolute; left: 12px; top: 10px; width: 24px; height: 24px; background: #3498db; color: white; border-radius: 50%; text-align: center; line-height: 24px; font-size: 10pt; font-weight: 700; }

        /* Connections */
        .connection-item { padding: 6px 12px; margin-bottom: 5px; background: #edf2f7; border-radius: 4px; font-size: 10pt; border-left: 3px solid #2c3e50; }
        .connection-arrow { color: #3498db; font-weight: 700; margin: 0 6px; }

        /* Notes & remarks */
        .note-box { background: #fef9e7; border-left: 4px solid #f39c12; padding: 12px 15px; margin: 10px 0; border-radius: 0 6px 6px 0; font-size: 10pt; }
        .info-box { background: #eaf2f8; border-left: 4px solid #3498db; padding: 12px 15px; margin: 10px 0; border-radius: 0 6px 6px 0; font-size: 10pt; }

        /* Signature block */
        .signature-block { margin-top: 40px; display: flex; justify-content: space-between; }
        .signature-col { width: 45%; }
        .signature-line { border-top: 1px solid #2c3e50; margin-top: 40px; padding-top: 5px; font-size: 10pt; }
        .signature-label { font-size: 9pt; color: #7f8c8d; }

        /* Footer */
        .report-footer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #dce1e7; font-size: 8pt; color: #95a5a6; display: flex; justify-content: space-between; }

        /* Equation display */
        .equation { font-family: 'Cambria Math', 'Times New Roman', serif; font-size: 12pt; background: #f7f9fc; padding: 10px 15px; border-radius: 6px; margin: 8px 0; text-align: center; border: 1px solid #dce1e7; }

        @media print { .page { padding: 20px; } .section { page-break-inside: avoid; } }
    """

    @staticmethod
    def _esc(value):
        """Escape HTML entities for safe rendering."""
        if value is None:
            return 'N/A'
        return escape(str(value))

    @staticmethod
    def _generate_report_id():
        """Generate a unique report ID."""
        now = datetime.now()
        return f"RPT-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

    @classmethod
    def generate_calculation_report(cls, content: dict) -> dict:
        """Generate a professional technical report for engineering calculations."""
        try:
            report_id = cls._generate_report_id()
            now = datetime.now()
            e = cls._esc

            # Build input rows
            inputs_html = ""
            for k, v in content.get('inputs', {}).items():
                unit = content.get('input_units', {}).get(k, '')
                inputs_html += f"""
                    <tr><td>{e(k)}</td><td>{e(v)}</td><td>{e(unit)}</td></tr>
                """

            # Build result cards
            results_html = ""
            for k, v in content.get('results', {}).items():
                unit = content.get('result_units', {}).get(k, '')
                results_html += f"""
                    <div class="result-card">
                        <div class="label">{e(k)}</div>
                        <div class="value">{e(v)}</div>
                        <div class="unit">{e(unit)}</div>
                    </div>
                """

            # Compliance status
            compliance = content.get('compliance', {})
            if isinstance(compliance, str):
                compliance = {'status': compliance}
            comp_status = compliance.get('status', 'N/A')
            comp_class = 'badge-pass' if comp_status.lower() in ('pass', 'compliant', 'ok') else \
                         'badge-fail' if comp_status.lower() in ('fail', 'non-compliant', 'failed') else 'badge-info'

            # Standards
            standards = content.get('standards', [])
            if isinstance(standards, str):
                standards = [standards]
            standards_html = ", ".join(e(s) for s in standards) if standards else "N/A"

            # Equation
            equation = content.get('equation', '')
            equation_html = f'<div class="equation">{e(equation)}</div>' if equation else ''

            # Methodology steps
            methodology = content.get('methodology', [])
            methodology_html = ""
            if methodology:
                methodology_html = '<ol class="step-list">'
                for step in methodology:
                    methodology_html += f'<li class="step-item">{e(step)}</li>'
                methodology_html += '</ol>'

            # AI explanation
            ai_explanation = content.get('ai_explanation', '')
            ai_html = f'<div class="info-box">{e(ai_explanation)}</div>' if ai_explanation else ''

            # Remarks
            remarks = content.get('remarks', '')
            remarks_html = f'<div class="note-box">{e(remarks)}</div>' if remarks else ''

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{e(content.get('title', 'Engineering Calculation Report'))}</title>
    <style>{cls.REPORT_CSS}</style>
</head>
<body>
<div class="page">
    <!-- Header -->
    <div class="report-header">
        <div class="header-left">
            <div class="report-title">{e(content.get('title', 'Engineering Calculation Report'))}</div>
            <div class="report-subtitle">{e(content.get('subtitle', 'Technical Calculation Sheet'))}</div>
            <div class="report-id">{report_id}</div>
        </div>
        <div class="header-right">
            <strong>EngiSuite Analytics Pro</strong><br>
            {now.strftime('%B %d, %Y')}<br>
            Rev. {e(content.get('revision', '0'))}
        </div>
    </div>

    <!-- Project Information -->
    <div class="section">
        <div class="section-title">1. Project Information</div>
        <table class="meta-table">
            <tr><td>Project Name</td><td>{e(content.get('project_name', 'N/A'))}</td></tr>
            <tr><td>Location</td><td>{e(content.get('location', 'N/A'))}</td></tr>
            <tr><td>Client</td><td>{e(content.get('client', 'N/A'))}</td></tr>
            <tr><td>Engineer</td><td>{e(content.get('engineer_name', 'N/A'))}</td></tr>
            <tr><td>Calculation Type</td><td>{e(content.get('calc_type', 'N/A'))}</td></tr>
            <tr><td>Discipline</td><td>{e(content.get('discipline', 'N/A'))}</td></tr>
            <tr><td>Reference Standards</td><td>{standards_html}</td></tr>
            <tr><td>Date</td><td>{e(content.get('date', now.strftime('%Y-%m-%d')))}</td></tr>
        </table>
    </div>

    <!-- Design Basis / Equation -->
    <div class="section">
        <div class="section-title">2. Design Basis</div>
        {equation_html}
        {methodology_html if methodology_html else '<p>Standard engineering methodology applied per referenced standards.</p>'}
    </div>

    <!-- Input Parameters -->
    <div class="section">
        <div class="section-title">3. Input Parameters</div>
        <table class="data-table">
            <thead><tr><th>Parameter</th><th>Value</th><th>Unit</th></tr></thead>
            <tbody>{inputs_html if inputs_html else '<tr><td colspan="3">No input parameters specified</td></tr>'}</tbody>
        </table>
    </div>

    <!-- Calculation Results -->
    <div class="section">
        <div class="section-title">4. Calculation Results</div>
        <div class="result-grid">
            {results_html if results_html else '<div class="result-card"><div class="label">Status</div><div class="value">Pending</div></div>'}
        </div>
    </div>

    <!-- Compliance Check -->
    <div class="section">
        <div class="section-title">5. Compliance &amp; Standards Check</div>
        <table class="meta-table">
            <tr><td>Compliance Status</td><td><span class="badge {comp_class}">{e(comp_status)}</span></td></tr>
            <tr><td>Applicable Standards</td><td>{standards_html}</td></tr>
            <tr><td>Notes</td><td>{e(compliance.get('notes', 'N/A'))}</td></tr>
        </table>
    </div>

    <!-- AI Analysis -->
    {'<div class="section"><div class="section-title">6. AI-Powered Analysis</div>' + ai_html + '</div>' if ai_explanation else ''}

    <!-- Remarks -->
    {'<div class="section"><div class="section-title">7. Remarks &amp; Recommendations</div>' + remarks_html + '</div>' if remarks else ''}

    <!-- Signature Block -->
    <div class="signature-block">
        <div class="signature-col">
            <div class="signature-line">
                <strong>{e(content.get('engineer_name', 'Prepared By'))}</strong><br>
                <span class="signature-label">Prepared By / Date</span>
            </div>
        </div>
        <div class="signature-col">
            <div class="signature-line">
                <strong>{e(content.get('reviewer_name', 'Reviewed By'))}</strong><br>
                <span class="signature-label">Reviewed By / Date</span>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="report-footer">
        <span>{report_id}</span>
        <span>EngiSuite Analytics Pro - Confidential</span>
        <span>{now.strftime('%Y-%m-%d %H:%M')}</span>
    </div>
</div>
</body>
</html>"""

            return {"html": html, "report_id": report_id, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    @classmethod
    def generate_workflow_report(cls, content: dict) -> dict:
        """Generate a professional technical report for workflow execution."""
        try:
            report_id = cls._generate_report_id()
            now = datetime.now()
            e = cls._esc

            nodes = content.get('nodes', [])
            connections = content.get('connections', [])
            execution_order = content.get('execution_order', [])

            # Execution order
            order_html = '<ol class="step-list">'
            for name in execution_order:
                order_html += f'<li class="step-item">{e(name)}</li>'
            order_html += '</ol>'

            # Node details
            nodes_html = ""
            for i, node in enumerate(nodes):
                inputs_rows = ""
                for k, v in node.get('inputs', {}).items():
                    inputs_rows += f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>"

                outputs_rows = ""
                for k, v in node.get('outputs', {}).items():
                    outputs_rows += f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>"

                status = node.get('status', 'completed')
                status_class = 'badge-pass' if status == 'completed' else 'badge-fail' if status == 'error' else 'badge-info'

                nodes_html += f"""
                <div class="section" style="margin-left: 15px;">
                    <div class="subsection-title">
                        Node {i+1}: {e(node.get('name', 'Unknown'))}
                        <span class="badge {status_class}" style="margin-left: 10px;">{e(status)}</span>
                    </div>
                    <p style="font-size: 9pt; color: #7f8c8d; margin-bottom: 8px;">Type: {e(node.get('type', 'N/A'))}</p>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div class="subsection-title" style="font-size: 10pt;">Input Parameters</div>
                            <table class="data-table">
                                <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
                                <tbody>{inputs_rows if inputs_rows else '<tr><td colspan="2">No inputs</td></tr>'}</tbody>
                            </table>
                        </div>
                        <div>
                            <div class="subsection-title" style="font-size: 10pt;">Output Results</div>
                            <table class="data-table">
                                <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
                                <tbody>{outputs_rows if outputs_rows else '<tr><td colspan="2">Not calculated</td></tr>'}</tbody>
                            </table>
                        </div>
                    </div>
                </div>"""

            # Connections
            connections_html = ""
            for conn in connections:
                connections_html += f"""
                <div class="connection-item">
                    {e(conn.get('from', 'Source'))}
                    <span class="connection-arrow">&rarr;</span>
                    {e(conn.get('to', 'Target'))}
                </div>"""

            # Summary stats
            total_nodes = len(nodes)
            completed_nodes = sum(1 for n in nodes if n.get('status', 'completed') == 'completed')
            error_nodes = sum(1 for n in nodes if n.get('status') == 'error')

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Workflow Execution Report</title>
    <style>{cls.REPORT_CSS}</style>
</head>
<body>
<div class="page">
    <!-- Header -->
    <div class="report-header">
        <div class="header-left">
            <div class="report-title">Workflow Execution Report</div>
            <div class="report-subtitle">{e(content.get('title', 'Engineering Workflow Analysis'))}</div>
            <div class="report-id">{report_id}</div>
        </div>
        <div class="header-right">
            <strong>EngiSuite Analytics Pro</strong><br>
            {now.strftime('%B %d, %Y %H:%M')}<br>
        </div>
    </div>

    <!-- Project Info -->
    <div class="section">
        <div class="section-title">1. Project Information</div>
        <table class="meta-table">
            <tr><td>Project Name</td><td>{e(content.get('project_name', 'N/A'))}</td></tr>
            <tr><td>Engineer</td><td>{e(content.get('engineer_name', 'N/A'))}</td></tr>
            <tr><td>Execution Date</td><td>{now.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        </table>
    </div>

    <!-- Summary -->
    <div class="section">
        <div class="section-title">2. Execution Summary</div>
        <div class="result-grid">
            <div class="result-card">
                <div class="label">Total Nodes</div>
                <div class="value">{total_nodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Completed</div>
                <div class="value" style="color: #27ae60;">{completed_nodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Errors</div>
                <div class="value" style="color: {'#e74c3c' if error_nodes > 0 else '#27ae60'};">{error_nodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Connections</div>
                <div class="value">{len(connections)}</div>
            </div>
        </div>
    </div>

    <!-- Execution Order -->
    <div class="section">
        <div class="section-title">3. Execution Order</div>
        {order_html if execution_order else '<p>No execution order determined.</p>'}
    </div>

    <!-- Node Details -->
    <div class="section">
        <div class="section-title">4. Node Details &amp; Results</div>
        {nodes_html if nodes_html else '<p>No nodes in workflow.</p>'}
    </div>

    <!-- Data Flow -->
    <div class="section">
        <div class="section-title">5. Data Flow Connections</div>
        {connections_html if connections_html else '<p>No connections defined.</p>'}
    </div>

    {'<div class="section"><div class="section-title">6. Notes</div><div class="note-box">' + e(content.get("error", "")) + '</div></div>' if content.get("error") else ''}

    <!-- Signature Block -->
    <div class="signature-block">
        <div class="signature-col">
            <div class="signature-line">
                <strong>{e(content.get('engineer_name', 'Prepared By'))}</strong><br>
                <span class="signature-label">Prepared By / Date</span>
            </div>
        </div>
        <div class="signature-col">
            <div class="signature-line">
                <strong>Reviewed By</strong><br>
                <span class="signature-label">Reviewed By / Date</span>
            </div>
        </div>
    </div>

    <div class="report-footer">
        <span>{report_id}</span>
        <span>EngiSuite Analytics Pro - Confidential</span>
        <span>{now.strftime('%Y-%m-%d %H:%M')}</span>
    </div>
</div>
</body>
</html>"""

            return {"html": html, "report_id": report_id, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    @classmethod
    def generate_analytics_report(cls, content: dict) -> dict:
        """Generate a professional data analytics / site report."""
        try:
            report_id = cls._generate_report_id()
            now = datetime.now()
            e = cls._esc

            # Summary stats
            summary = content.get('summary', {})
            summary_cards = ""
            for k, v in summary.items():
                summary_cards += f"""
                    <div class="result-card">
                        <div class="label">{e(k)}</div>
                        <div class="value">{e(v)}</div>
                    </div>"""

            # Data table
            columns = content.get('columns', [])
            data_rows = content.get('data', [])
            table_html = ""
            if columns and data_rows:
                header = "".join(f"<th>{e(c)}</th>" for c in columns)
                rows = ""
                for row in data_rows[:100]:  # Limit to 100 rows in report
                    cells = "".join(f"<td>{e(row.get(c, ''))}</td>" for c in columns)
                    rows += f"<tr>{cells}</tr>"
                table_html = f"""
                    <table class="data-table">
                        <thead><tr>{header}</tr></thead>
                        <tbody>{rows}</tbody>
                    </table>
                    {'<p style="font-size: 9pt; color: #95a5a6;">Showing first 100 of ' + str(len(data_rows)) + ' rows</p>' if len(data_rows) > 100 else ''}
                """

            # Column statistics
            col_stats = content.get('column_stats', [])
            stats_html = ""
            if col_stats:
                stats_rows = ""
                for cs in col_stats:
                    stats_rows += f"""<tr>
                        <td>{e(cs.get('name', ''))}</td>
                        <td>{e(cs.get('type', ''))}</td>
                        <td>{e(cs.get('null_count', 0))}</td>
                        <td>{e(cs.get('unique_count', ''))}</td>
                        <td>{e(cs.get('min', ''))}</td>
                        <td>{e(cs.get('max', ''))}</td>
                        <td>{e(cs.get('mean', ''))}</td>
                    </tr>"""
                stats_html = f"""
                    <table class="data-table">
                        <thead><tr><th>Column</th><th>Type</th><th>Nulls</th><th>Unique</th><th>Min</th><th>Max</th><th>Mean</th></tr></thead>
                        <tbody>{stats_rows}</tbody>
                    </table>
                """

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Analytics Report</title>
    <style>{cls.REPORT_CSS}</style>
</head>
<body>
<div class="page">
    <div class="report-header">
        <div class="header-left">
            <div class="report-title">Data Analytics Report</div>
            <div class="report-subtitle">{e(content.get('title', 'Engineering Data Analysis'))}</div>
            <div class="report-id">{report_id}</div>
        </div>
        <div class="header-right">
            <strong>EngiSuite Analytics Pro</strong><br>
            {now.strftime('%B %d, %Y')}<br>
        </div>
    </div>

    <div class="section">
        <div class="section-title">1. Report Overview</div>
        <table class="meta-table">
            <tr><td>Data Source</td><td>{e(content.get('data_source', 'N/A'))}</td></tr>
            <tr><td>Template</td><td>{e(content.get('template', 'Custom'))}</td></tr>
            <tr><td>Generated</td><td>{now.strftime('%Y-%m-%d %H:%M')}</td></tr>
            <tr><td>Total Rows</td><td>{e(summary.get('row_count', 'N/A'))}</td></tr>
            <tr><td>Total Columns</td><td>{e(summary.get('column_count', 'N/A'))}</td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">2. Key Metrics</div>
        <div class="result-grid">
            {summary_cards if summary_cards else '<div class="result-card"><div class="label">Status</div><div class="value">No Data</div></div>'}
        </div>
    </div>

    {'<div class="section"><div class="section-title">3. Column Statistics</div>' + stats_html + '</div>' if stats_html else ''}

    {'<div class="section"><div class="section-title">4. Data Table</div>' + table_html + '</div>' if table_html else ''}

    <div class="report-footer">
        <span>{report_id}</span>
        <span>EngiSuite Analytics Pro</span>
        <span>{now.strftime('%Y-%m-%d %H:%M')}</span>
    </div>
</div>
</body>
</html>"""

            return {"html": html, "report_id": report_id, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    @classmethod
    def generate_pdf(cls, content: dict) -> dict:
        """Generate PDF from content (legacy method, now dispatches by report_type)."""
        report_type = content.get('report_type', 'calculation')

        if report_type == 'workflow':
            result = cls.generate_workflow_report(content)
        elif report_type == 'analytics':
            result = cls.generate_analytics_report(content)
        else:
            result = cls.generate_calculation_report(content)

        if not result.get('success'):
            return result

        try:
            import pdfkit
            pdf = pdfkit.from_string(result['html'], False)
            return {"pdf": pdf, "report_id": result['report_id'], "success": True}
        except Exception:
            # pdfkit/wkhtmltopdf not available, return HTML
            return result
