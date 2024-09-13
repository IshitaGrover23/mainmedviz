from django import forms

class UploadFileForm(forms.Form):
    pdf_file = forms.FileField(
        label='Select a PDF file',
        help_text='Upload a PDF file only.',
        allow_empty_file=False,
        widget=forms.FileInput(attrs={'accept': 'application/pdf'})
    )

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
        return pdf_file