from base import Text, FieldValidationError


class LxmlFieldValidationError(FieldValidationError):
	""" Auto-handlig of lxml validaton errors.

	Use this to when validating xml fields with lxml.
	"""
	def __init__(self, fieldname, value, offset, e):
		"""
		@param e: A lxml.etree.LxmlError object.
		"""
		err = []
		for log in e.error_log:
			err.append("%d: %s" % (offset + log.line, log.message))
		FieldValidationError.__init__(self, fieldname, value,
				"\n".join(err))


class XmlField(Text):
	""" A XML field with optional validation support. """
	def __init__(self, format="%s", offset=0, validate=None,
				required=True):
		r"""
		@param format: A string format to apply to the user input
				before validation. %s is replaced with the user input.
		@param offset: The linenumber in "format" where the user
				input begins.
		@param required: Boolean field is required?
		@param validate: A callable(fieldname, xml, offset) where xml is
				the user-input after "format" has been applied. The
				callable must raise L{FieldValidationError} if the
				validation fails. Note that L{LxmlFieldValidationError}
				is a subclass of FieldValidationError and can also be
				used.
		"""
		self.format = format
		self.offset = offset
		self.required = required
		self._findabetterway = [validate]

	def validate(self, fieldname, value):
		super(XmlField, self).validate(fieldname, value)
		if not value and not self.required:
			return
		validate = self._findabetterway[0]
		if validate != None:
			xml = self.format % value
			validate(fieldname, xml,
					self.offset)

class XhtmlField(XmlField):
	""" Exactly the same as L{XmlField}, except it indicates
	that the xml will be xhtml. """
